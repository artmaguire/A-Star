from Node import Node
from pg_helper import open_connection, close_connection, get_ways
import PriorityQueue as pq
import logging

from tag_check import get_tag_tuple

logger = logging.getLogger(__name__.split(".")[0])

open_connection()


def a_star(source, target):
    best_node = Node(source, 0, 0, 0, 0, None)

    visited_nodes = [source]
    closed_set = []

    tag_tuple = get_tag_tuple('car')

    while True:
        nodes = get_ways(best_node, tag_tuple, closed_set)
        pq.push_many(nodes)
        # visited_nodes.extend([n.node_id for n in nodes])

        best_node = pq.pop()
        logger.debug(best_node.__str__())

        closed_set.append(best_node.node_id)

        if best_node.node_id == target:
            break

    route = []

    while best_node is not None:
        route.append(best_node)
        best_node = best_node.previous

    route.reverse()

    s = [str(n.node_id) for n in route]
    st = "'" + "', '".join(s) + "'"
    logger.info(st)

    return route
