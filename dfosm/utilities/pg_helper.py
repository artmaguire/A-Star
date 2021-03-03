import psycopg2

from .. import classes
from .tags import Flags
from .geometry_helper import get_distance


class PGHelper:
    conn, curr = None, None

    def __init__(self, dbname, user, password, host, port, edges_table, vertices_table):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.edges_table = edges_table
        self.vertices_table = vertices_table

        self.open_connection()

    def open_connection(self):
        self.conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host,
                                     port=self.port)
        self.cur = self.conn.cursor()

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def get_node(self, node_id):
        query = """SELECT ST_X(geom_vertex), ST_Y(geom_vertex) FROM ie_vertices WHERE id=%s;"""

        self.cur.execute(query, (node_id,))
        node_tuple = self.cur.fetchone()

        return classes.Node(node_id, 0, 0, node_tuple[0], node_tuple[1])

    def get_ways(self, source: classes.Node, target: classes.Node, previous: classes.Node, flag: Flags, closed_set: tuple):
        query = """
        SELECT target, x2, y2, clazz, flags, cost, km, kmh, st_asgeojson(geom_way) FROM ie_edges WHERE source = %(source)s AND target != %(previous)s AND flags & %(flag)s != 0 AND target NOT IN %(closed)s
        UNION
        SELECT source, x1, y1, clazz, flags, cost, km, kmh, st_asgeojson(geom_way) FROM ie_edges WHERE target = %(source)s AND source != %(previous)s AND flags & %(flag)s != 0 AND reverse_cost < 1000000 AND source NOT IN %(closed)s
        """

        # Checks is previous node id is None - Only occurs for first node
        prev_id = -1 if previous is None else previous.node_id

        params = {
            'source':   source.node_id,
            'previous': prev_id,
            'flag':     flag.value,
            'closed':   closed_set
        }

        self.cur.execute(query, params)
        ways = self.cur.fetchall()

        nodes = [
            classes.Node(way[0], source.cost, way[5] * 60, way[1], way[2], km=way[6], kmh=way[7], distance=get_distance(way[1], way[2], target), previous=source, geojson=way[8])
            for way in ways]

        return nodes

    def find_nearest_road(self, lat, lng):
        query = """select tgt, src, st_asgeojson(geom) from dfosm_split_geometry(%s, %s);"""
        self.cur.execute(query, (lat, lng))
        node_tuples = self.cur.fetchall()

        nodes = []

        for node_tuple in node_tuples:
            dummy_node = classes.Node(node_tuple[1], 0, 0, 0, 0)
            node = classes.Node(node_tuple[0], 0, 0, 0, 0, 0, previous=dummy_node, geojson=node_tuple[2])
            nodes.append(node)

        return nodes[0], nodes[1]
