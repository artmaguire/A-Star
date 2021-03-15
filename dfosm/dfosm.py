import concurrent.futures
import logging
from time import time

# from .classes import PriorityQueue
from queue import PriorityQueue, Queue
from .classes import Node
from .utilities import Flags
from .utilities import PGHelper
from .astar import astar_manager, astar_worker

logger = logging.getLogger(__name__.split(".")[0])


class DFOSM:
    def __init__(self, dbname, dbuser, dbpassword, dbhost='127.0.0.1', dbport=5432, edges_table='edges',
                 vertices_table='vertices'):
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.dbhost = dbhost
        self.dbport = dbport
        self.edges_table = edges_table
        self.vertices_table = vertices_table

        self.pg = PGHelper(dbname, dbuser, dbpassword, dbhost, dbport, edges_table, vertices_table)

    def close_database(self):
        self.pg.put_connection()

    def a_star(self, source_lat, source_lng, target_lat, target_lng, visualisation=False, history=False):
        best_node, second_best_node = self.pg.find_nearest_road(source_lng, source_lat)

        target_node = Node(-1, 0, 0, target_lng, target_lat)

        target_node_a, target_node_b = self.pg.find_nearest_road(target_lng, target_lat)

        closed_node_dict = {best_node.node_id: best_node,
                            second_best_node.node_id: second_best_node}

        target_node_dict = {target_node_a.node_id: target_node_a,
                            target_node_b.node_id: target_node_b}

        pq = PriorityQueue()
        notify_queue = Queue(maxsize=2)
        pq.put(best_node)
        pq.put(second_best_node)

        history_list = [[best_node.serialize(), second_best_node.serialize()]] if history else None

        t0 = time()
        node_count = astar_manager(self.pg, pq, notify_queue, closed_node_dict, target_node,
                                   target_node_dict,
                                   Flags.CAR, history_list, workers=6)
        best_node = notify_queue.get()
        nearest_node = notify_queue.get()
        t1 = time()
        logger.info(f'A-Star workers time: {round(t1 - t0, 3)}s')

        target_node.geojson = nearest_node.geojson
        target_node.previous = best_node
        target_node.cost_minutes = best_node.cost_minutes
        best_node = target_node

        if history:
            history_list.append([best_node.serialize()])

        route = self._get_route_(best_node)

        to_return = {
            'route': self._route_to_str_(route),
            # 'start_point': route[0].lat + ',' + route[0].lng,
            'end_point': str(best_node.lat) + ',' + str(best_node.lng),
        }

        if history:
            to_return['history'] = history_list

        if visualisation:
            branch_routes = []
            Node.found_route = True
            # pq.heapify()

            best_branch_node = pq.get()

            while best_branch_node:
                branch = {'cost': best_branch_node.cost,
                          'distance': best_branch_node.distance,
                          'total_cost': best_branch_node.calculate_total_cost(),
                          'route': self._route_to_str_(self._get_route_(best_branch_node))}
                branch_routes.append(branch)
                # pq.heapify()

                best_branch_node = pq.get()

            to_return['branch'] = branch_routes

        logger.info('******************************************************')
        logger.info(f'Total Nodes Searched: {node_count}')
        logger.info(f'Nodes In Route: {len(route)}')
        logger.info(f'Estimated distance: {best_node.get_total_distance():.2f}km')
        logger.info(f'Estimated Time: {best_node.cost_minutes:.2f}m')

        return to_return

    def bi_a_star(self, source_lat, source_lng, target_lat, target_lng, visualisation=False, history=False):
        source_node = Node(0, 0, 0, source_lng, source_lat)
        best_node, second_best_node = self.pg.find_nearest_road(source_lng, source_lat)

        target_node = Node(-1, 0, 0, target_lng, target_lat)
        target_node_a, target_node_b = self.pg.find_nearest_road(target_lng, target_lat)

        closed_node_dict = {best_node.node_id: best_node,
                            second_best_node.node_id: second_best_node}
        source_pq = PriorityQueue()
        source_pq.put(best_node)
        source_pq.put(second_best_node)

        target_node_dict = {target_node_a.node_id: target_node_a,
                            target_node_b.node_id: target_node_b}
        target_pq = PriorityQueue()
        target_pq.put(target_node_a)
        target_pq.put(target_node_b)

        notify_queue = Queue(maxsize=2)

        history_list = [[best_node.serialize(), second_best_node.serialize(), target_node_a.serialize(),
                         target_node_b.serialize()]] if history else None

        t0 = time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            source_future = executor.submit(astar_manager, self.pg, source_pq, notify_queue, closed_node_dict,
                                            target_node, target_node_dict, Flags.CAR, history_list, 3)
            target_future = executor.submit(astar_manager, self.pg, target_pq, notify_queue, target_node_dict,
                                            source_node, closed_node_dict, Flags.CAR, history_list, 3)
            node_count = source_future.result() + target_future.result()
        best_node = notify_queue.get()
        middle_node = notify_queue.get()
        t1 = time()
        logger.info(f'Bidirectional A-Star workers time: {round(t1 - t0, 3)}s')

        # target_node.previous = best_node
        # target_node.cost_minutes = best_node.cost_minutes
        # best_node = target_node

        if history:
            history_list.append([best_node.serialize()])

        route = self._get_route_(best_node) + self._get_route_(middle_node)

        to_return = {
            'route': self._route_to_str_(route),
            # 'start_point': route[0].lat + ',' + route[0].lng,
            'end_point': str(best_node.lat) + ',' + str(best_node.lng),
        }

        if history:
            to_return['history'] = history_list

        if visualisation:
            branch_routes = []
            Node.found_route = True
            # pq.heapify()

            best_branch_node = source_pq.get()

            while best_branch_node:
                branch = {'cost': best_branch_node.cost,
                          'distance': best_branch_node.distance,
                          'total_cost': best_branch_node.calculate_total_cost(),
                          'route': self._route_to_str_(self._get_route_(best_branch_node))}
                branch_routes.append(branch)
                # pq.heapify()

                best_branch_node = source_pq.get()

            to_return['branch'] = branch_routes

        logger.info('******************************************************')
        logger.info(f'Total Nodes Searched: {node_count}')
        logger.info(f'Nodes In Route: {len(route)}')
        logger.info(f'Estimated distance: {best_node.get_total_distance():.2f}km')
        logger.info(f'Estimated Time: {best_node.cost_minutes:.2f}m')

        return to_return

    # X: longitude, Y: latitude
    def find_nearest_road(self, x, y):
        return self.pg.find_nearest_road(x, y)

    @staticmethod
    def _get_route_(node, reverse=True):
        route = []
        while node and node.geojson:
            route.append(node.geojson)
            node = node.get_previous()

        if reverse:
            route.reverse()
        return route

    @staticmethod
    def _route_to_str_(route):
        return '[' + ','.join(route) + ']'
