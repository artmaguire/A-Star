import psycopg2
from psycopg2 import pool

from .. import classes
from .constants import Flags
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

        self.conn_pool = psycopg2.pool.ThreadedConnectionPool(12, 100, dbname=self.dbname, user=self.user,
                                                              password=self.password, host=self.host,
                                                              port=self.port)

        self.conn = self.get_connection()

    def get_connection(self):
        conn = self.conn_pool.getconn()
        conn.autocommit = True
        return conn

    def put_connection(self, conn=None):
        if conn is None:
            conn = self.conn
        self.conn_pool.putconn(conn)

    def close_all_connections(self):
        self.conn_pool.closeall()

    def get_node(self, node_id):
        with self.conn.cursor() as cur:
            query = """SELECT ST_X(geom_vertex), ST_Y(geom_vertex) FROM ie_vertices WHERE id=%s;"""

            cur.execute(query, (node_id,))
            node_tuple = cur.fetchone()

        return classes.Node(node_id, 0, 0, node_tuple[0], node_tuple[1])

    def get_ways(self, source: classes.Node, target: classes.Node, flag: Flags, closed_set: tuple, conn=None):
        if conn is None:
            conn = self.conn
        with conn.cursor() as cur:
            query = """
            SELECT target, x2, y2, clazz, flags, cost, km, kmh, st_asgeojson(geom_way) FROM ie_edge WHERE source = %(source)s AND flags & %(flag)s != 0 AND target NOT IN %(closed)s
            UNION
            SELECT source, x1, y1, clazz, flags, cost, km, kmh, st_asgeojson(geom_way) FROM ie_edge WHERE target = %(source)s AND flags & %(flag)s != 0 AND reverse_cost < 1000000 AND source NOT IN %(closed)s
            """

            # Checks is previous node id is None - Only occurs for first node

            params = {
                'source': source.node_id,
                'flag': flag.value,
                'closed': closed_set
            }

            cur.execute(query, params)
            ways = cur.fetchall()

        nodes = [
            classes.Node(way[0], source.cost, way[5] * 60, way[1], way[2], km=way[6], kmh=way[7],
                         distance=get_distance(way[2], way[1], target.lat, target.lng), previous=source, geojson=way[8])
            for way in ways]

        return nodes

    def find_closest_point_on_edge(self, x, y, flag):
        with self.conn.cursor() as cur:
            query = """select lat, lng, geom_id, on_vertix from dfosm_find_closest_point_on_edge(%s, %s, %s);"""
            cur.execute(query, (x, y, flag))
            result = cur.fetchone()
        return result

    def find_nearest_road(self, x, y, edge_id):
        with self.conn.cursor() as cur:
            query = """select tgt, src, st_asgeojson(geom) from dfosm_split_geometry(%s, %s, %s);"""
            cur.execute(query, (x, y, edge_id))
            node_tuples = cur.fetchall()

        nodes = []

        for node_tuple in node_tuples:
            node = classes.Node(node_tuple[0], 0, 0, 0, 0, 0, geojson=node_tuple[2])
            nodes.append(node)

        return nodes[0], nodes[1]
