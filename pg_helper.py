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


def get_ways(source: Node, visited_nodes):
    query = """SELECT source, target, cost, x1, y1, x2, y2 FROM ways WHERE ways.target = %s OR ways.source = %s"""

    cur.execute(query, (source.node_id, source.node_id))
    ways = cur.fetchall()

    nodes = []

    for way in ways:
        if way[0] == source.node_id:
            node_id, lat, lng = way[1], way[5], way[6]
        else:
            node_id, lat, lng = way[0], way[3], way[4]

        if source.previous is not None and node_id == source.previous.node_id:
            continue

        if node_id in visited_nodes:
            continue

        nodes.append(Node(node_id, (source.cost + way[2]), lat, lng, 0, source))

    return nodes
