from Node import Node
from pg_helper import open_connection, close_connection, get_node, get_ways
import PriorityQueue as pq
import logging

from tag_check import get_tag_tuple

logger = logging.getLogger(__name__.split(".")[0])

open_connection()


def a_star(source_id, target_id):
    best_node = get_node(source_id)
    target_node = get_node(target_id)

    closed_set = [source_id]

    tag_tuple = get_tag_tuple('car')

    while True:
        nodes = get_ways(best_node, tag_tuple, closed_set, target_node)
        pq.push_many(nodes)

        best_node = pq.pop()
        logger.debug(best_node.__str__())

        closed_set.append(best_node.node_id)

        if best_node.node_id == target_id:
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
