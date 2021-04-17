import json

import psycopg2
from psycopg2 import pool

from dfosm import classes
from ..utilities.constants import Flags
from ..utilities.geometry_helper import get_distance


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

        return classes.Node(node_id=node_id, lng=node_tuple[0], lat=node_tuple[1])

    def get_ways(self, source: classes.Node, target: classes.Node, flag: Flags, closed_set: tuple,
                 node_options: classes.NodeOptions, reverse_direction: bool, min_clazz=256, conn=None):
        if conn is None:
            conn = self.conn
        with conn.cursor() as cur:
            query = """
            SELECT target, x2, y2, clazz, flags, cost, km, kmh, st_asgeojson(geom_way) FROM ie_edge WHERE source = %(source)s AND flags & %(flag)s != 0 AND reverse_cost < %(reverse_cost_source)s AND target NOT IN %(closed)s AND clazz <= %(min_clazz)s
            UNION
            SELECT source, x1, y1, clazz, flags, cost, km, kmh, st_asgeojson(geom_way) FROM ie_edge WHERE target = %(source)s AND flags & %(flag)s != 0 AND reverse_cost < %(reverse_cost_target)s AND source NOT IN %(closed)s AND clazz <= %(min_clazz)s
            """

            reverse_cost_source = 1000000 if reverse_direction else 10000000
            reverse_cost_target = 10000000 if reverse_direction else 1000000

            params = {
                'source':              source.node_id,
                'flag':                flag,
                'closed':              closed_set,
                'reverse_cost_source': reverse_cost_source,
                'reverse_cost_target': reverse_cost_target,
                'min_clazz':           min_clazz
            }

            cur.execute(query, params)
            ways = cur.fetchall()

        nodes = []
        for way in ways:
            kmh, cost = cost_modifier(flag, way[6], way[7], way[5])
            nodes.append(
                    classes.Node(node_id=way[0], clazz=way[3], initial_cost=cost * 60, lng=way[1], lat=way[2],
                                 km=way[6],
                                 kmh=kmh,
                                 distance=get_distance(way[2], way[1], target.lat, target.lng), previous=source,
                                 geojson=json.loads(way[8]),
                                 node_options=node_options))

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
            node = classes.Node(node_id=node_tuple[0], geojson=json.loads(node_tuple[2]))
            nodes.append(node)

        return nodes[0], nodes[1]


def cost_modifier(flag, km, kmh, cost):
    BIKE_MAX_SPEED = 30
    WALK_MAX_SPEED = 5

    if flag == Flags.BIKE.value:
        if kmh > BIKE_MAX_SPEED:
            return BIKE_MAX_SPEED, (km / BIKE_MAX_SPEED)
    elif flag == Flags.FOOT.value:
        if kmh > WALK_MAX_SPEED:
            return WALK_MAX_SPEED, (km / WALK_MAX_SPEED)

    return kmh, cost
