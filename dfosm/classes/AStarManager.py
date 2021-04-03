import concurrent.futures

import logging
import queue

from .NodeOptions import NodeOptions

logger = logging.getLogger(__name__.split(".")[0])


class AStarManager:
    def __init__(self, pg, pq, notify_queue, closed_node_dict, target_node_dict, target_node, flag=1, history_list=None,
                 workers=6, node_options=NodeOptions(), min_clazz=256, reverse_direction=False):
        self.pg = pg
        self.pq = pq
        self.notify_queue = notify_queue
        self.closed_node_dict = closed_node_dict
        self.target_node_dict = target_node_dict
        self.target_node = target_node
        self.flag = flag
        self.history_list = history_list
        self.workers = workers
        self.node_options = node_options
        self.min_clazz = min_clazz
        self.reverse_direction = reverse_direction

    def run(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.astar_worker, i) for i in range(self.workers)]
            node_count = sum(f.result() for f in futures)
        return node_count

    def astar_worker(self, idx):
        logger.debug(f'Worker: {idx} starting')
        conn = self.pg.get_connection()
        node_count = 0
        while True:
            try:
                best_node = self.pq.get(timeout=5)
            except queue.Empty:
                logger.debug(f'Priority Queue is empty. Worker {idx} quitting.')
                break
            self.closed_node_dict[best_node.node_id] = best_node

            # To keep it within 20 kilometers from limerick
            if best_node.cost_minutes > 60:
                break

            # logger.debug(best_node.__str__())

            nodes = self.pg.get_ways(best_node, self.target_node, self.flag, tuple(self.closed_node_dict),
                                     self.node_options, self.reverse_direction, min_clazz=self.min_clazz, conn=conn)

            if self.history_list:
                self.history_list.append([node.serialize() for node in nodes])
            for node in nodes:
                if node.node_id in self.target_node_dict:
                    d = {
                        0: node,
                        1: self.target_node_dict[node.node_id]
                    }
                    self.notify_queue.put(d, block=False)
                    break
                self.pq.put(node, block=False)

            if not self.notify_queue.empty():
                break

            node_count += 1

        self.pg.put_connection(conn)
        return node_count
