import concurrent.futures
import logging
import queue
from time import time

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
        end_count = 0
        t0 = time()

        while True:
            try:
                best_node = self.pq.get(timeout=5)
            except queue.Empty:
                logger.warning(f'Priority Queue is empty. Worker {idx} quitting.')
                break

            if best_node.node_id in self.target_node_dict:
                d = (
                    best_node,
                    self.target_node_dict[best_node.node_id]['node']
                )
                self.notify_queue.put(d, block=False)

            closed_node_dict = tuple(self.closed_node_dict[best_node.node_id]['neighbours'])

            nodes = self.pg.get_ways(best_node, self.target_node, self.flag, tuple(closed_node_dict),
                                     self.node_options, self.reverse_direction, min_clazz=self.min_clazz, conn=conn)

            if self.history_list:
                self.history_list.append([node.serialize() for node in nodes])
            for node in nodes:
                if node.node_id in self.closed_node_dict:
                    self.closed_node_dict[node.node_id]['neighbours'].append(best_node.node_id)
                    existing_node = self.closed_node_dict[node.node_id]['node']
                    if node.cost_minutes < existing_node.cost_minutes:
                        logger.debug(f'Worker {idx} found a better branch: {existing_node} -> {node}')
                        existing_node.previous = best_node
                        existing_node.cost = node.cost
                        existing_node.cost_minutes = node.cost_minutes
                        existing_node.distance_minutes = node.distance_minutes
                        existing_node.total_cost = node.total_cost
                        existing_node.km = node.km
                        existing_node.kmh = node.kmh
                        existing_node.geojson = node.geojson
                else:
                    self.closed_node_dict[node.node_id] = {'node': node, 'neighbours': [best_node.node_id]}
                    self.pq.put(node, block=False)

            if not self.notify_queue.empty():
                end_count += 1

            if end_count > 30:
                break

            node_count += 1

            if not (node_count % 10000):
                logger.debug(f'Worker {idx} has checked {node_count} nodes after {(time() - t0):.2f}s.')

        self.pg.put_connection(conn)
        return node_count


def all_roads_worker(pg, pq, end_nodes_pq, closed_node_dict, target_node, flag=1,
                     history_list=None, node_options=NodeOptions(), min_clazz=256, reverse_direction=False):
    conn = pg.get_connection()
    node_count = 0
    end_nodes_dict = {}

    while True:
        try:
            best_node = pq.get(timeout=5)
        except queue.Empty:
            logger.debug(f'Priority Queue is empty. Worker quitting.')
            break
        closed_node_dict[best_node.node_id] = best_node

        # To keep it within 20 kilometers from limerick
        # if best_node.cost_minutes > 60:
        #     break

        # logger.debug(best_node.__str__())

        nodes = pg.get_ways(best_node, target_node, flag, (1,),
                            node_options, reverse_direction, min_clazz=min_clazz, conn=conn)

        if history_list:
            history_list.append([node.serialize() for node in nodes])

        if not nodes:
            end_nodes_dict[best_node.node_id] = best_node
            end_nodes_pq.put(best_node, block=False)

        for node in nodes:
            # closed_node_dict[node.node_id] = node
            if node.node_id in closed_node_dict:
                continue

            if node.node_id in end_nodes_dict:
                end_nodes_dict[best_node.node_id] = best_node
                end_nodes_pq.put(best_node, block=False)
                continue

            pq.put(node, block=False)

        node_count += 1

    pg.put_connection(conn)
    return node_count
