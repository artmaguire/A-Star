import psycopg2
from math import sin, cos, sqrt, atan2, radians
from config import conf
from Node import Node


def open_connection():
    global conn, cur
    conn = psycopg2.connect(dbname=conf.DBNAME, user=conf.DBUSER, password=conf.DBPASSWORD, host=conf.DBHOST,
                            port=conf.DBPORT)
    cur = conn.cursor()


def close_connection():
    cur.close()
    conn.close()


def get_node(node_id):
    query = """SELECT * FROM nz_ways_vertices_pgr WHERE id = %s;"""

    cur.execute(query, (node_id,))
    node_tuple = cur.fetchall()

    return Node(node_id, 0, node_tuple[0][3], node_tuple[0][4], 0, None)


def get_ways(source: Node, tag_tuple: str, closed_set, target: Node):
    query = """SELECT source, target, cost_s, x1, y1, x2, y2, one_way FROM nz_ways WHERE (target = %s OR source = %s) AND 
        tag_id in %s"""

    cur.execute(query, (source.node_id, source.node_id, tag_tuple))
    ways = cur.fetchall()

    nodes = []

    for way in ways:
        if way[0] == source.node_id:
            node_id, lat, lng = way[1], way[5], way[6]
        else:
            node_id, lat, lng = way[0], way[3], way[4]

        # Ensure we don't go straight back to the node we came from
        if source.previous is not None and node_id == source.previous.node_id:
            continue

        # Already been the this node by a lower cost route
        if node_id in closed_set:
            continue

        # Check if one_way road and we are going in the right direction
        # We do this by checking if we are at the source (start) of the one way road, and not the target (end)
        # Also works for roundabouts
        if way[7] == 1 and source.node_id != way[0]:
            continue

        nodes.append(
                Node(node_id, source.cost + way[2], lat, lng, get_distance(lat, lng, target), source))

    return nodes


def get_distance(lat, lng, target):
    # approximate radius of earth in km
    R = 6378.0

    source_lat, source_lng = radians(lat), radians(lng)
    target_lat, target_lng = radians(target.lat), radians(target.lng)

    diff_lat = target_lat - source_lat
    diff_lng = target_lng - source_lng

    # Formula for getting distance between (lat, lng): d = acos( sin φ1 ⋅ sin φ2 + cos φ1 ⋅ cos φ2 ⋅ cos Δλ ) ⋅ R
    a = sin(diff_lat / 2) ** 2 + cos(source_lat) * cos(target_lat) * sin(diff_lng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance
