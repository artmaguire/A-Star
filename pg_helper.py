import psycopg2

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


def get_ways(source: Node, tag_tuple: str, closed_set):
    query = """SELECT source, target, cost_s, x1, y1, x2, y2, one_way FROM ways WHERE (ways.target = %s OR ways.source = %s) AND 
        ways.tag_id in %s"""

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

        nodes.append(Node(node_id, source.cost + way[2], lat, lng, 0, source))

    return nodes


def get_distance(node_id, target_id):
    query = """select st_distance(ST_TRANSFORM((SELECT the_geom FROM ways WHERE ways.target = %s OR ways.source = %s LIMIT 1), 4351), ST_TRANSFORM((SELECT the_geom FROM ways WHERE ways.target = %s OR ways.source = %s LIMIT 1), 4351), true)"""

    cur.execute(query, (node_id, node_id, target_id, target_id))
    distances = cur.fetchall()

    distance = float(distances[0][0])

    return distance / 1000
