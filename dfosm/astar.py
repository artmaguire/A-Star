import concurrent.futures

import logging

logger = logging.getLogger(__name__.split(".")[0])


def astar_manager(pg, pq, notify_queue, closed_node_dict, target_node, target_node_dict, flag=1, history_list=None, workers=6):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(astar_worker, pg, pq, notify_queue, closed_node_dict, target_node,
                                   target_node_dict, flag, history_list) for _ in range(workers)]
        node_count = sum(f.result() for f in futures)
    return node_count


def astar_worker(pg, pq, notify_queue, closed_node_dict, target_node, target_node_dict, flag=1, history_list=None):
    conn = pg.get_connection()
    node_count = 0
    while True:
        best_node = pq.get()
        closed_node_dict[best_node.node_id] = best_node

        logger.debug(best_node.__str__())

        nodes = pg.get_ways(best_node, target_node, flag, tuple(closed_node_dict), conn=conn)

        if history_list:
            history_list.append([node.serialize() for node in nodes])
        for node in nodes:
            if node.node_id in target_node_dict:
                notify_queue.put(node)
                notify_queue.put(target_node_dict[node.node_id])
                break
            pq.put(node, block=False)

        if not notify_queue.empty():
            break

        node_count += 1

    pg.put_connection(conn)
    return node_count
