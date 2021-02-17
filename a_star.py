from Node import Node
from pg_helper import open_connection, close_connection, get_ways
import PriorityQueue as pq
import logging

logger = logging.getLogger(__name__)

open_connection()


def a_star(source, target):
    best_node = Node(source, 0, 0, 0, 0, None)

    visited_nodes = [source]
    closed_set = []

    while True:
        nodes = get_ways(best_node, visited_nodes)
        pq.push_many(nodes)
        visited_nodes.extend([n.node_id for n in nodes])

        best_node = pq.pop()
        logger.debug(best_node.__str__())

        closed_set.append(best_node)

        if best_node.node_id == target:
            break

    route = []
    current_node = closed_set[-1]

    while current_node is not None:
        route.append(current_node)

        current_node = current_node.previous

    route.reverse()
    logger.info(route)

    s = [str(n.node_id) for n in route]
    st = "', '".join(s)
    logger.info(st)

    return route
