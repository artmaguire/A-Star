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
        end_poi_lat, end_poi_lng, geom_id, on_vertix = self.pg.find_closest_point_on_edge(target_lng, target_lat,
                                                                                              Flags.CAR.value)

        target_node = Node(-1, 0, 0, end_poi_lng, end_poi_lat)

        if on_vertix:
            end_nodes = self.pg.get_ways(Node(geom_id, 0, 0, 0, 0), target_node, Flags.CAR, (geom_id,))
        else:
            end_nodes = self.pg.find_nearest_road(end_poi_lng, end_poi_lat, geom_id)

        start_poi_lat, start_poi_lng, geom_id, on_vertix = self.pg.find_closest_point_on_edge(source_lng, source_lat, Flags.CAR.value)
        if on_vertix:
            start_nodes = self.pg.get_ways(Node(geom_id, 0, 0, 0, 0), target_node, Flags.CAR, (geom_id,))
        else:
            start_nodes = self.pg.find_nearest_road(start_poi_lng, start_poi_lat, geom_id)

        closed_node_dict = {node.node_id: node for node in start_nodes}

        target_node_dict = {node.node_id: node for node in end_nodes}

        pq = PriorityQueue()
        notify_queue = Queue()
        for node in start_nodes:
            pq.put(node)

        history_list = [[node.serialize() for node in start_nodes]] if history else None

        t0 = time()
        node_count = astar_manager(self.pg, pq, notify_queue, closed_node_dict, target_node,
                                   target_node_dict,
                                   Flags.CAR, history_list, workers=1)
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
            'start_point': str(start_poi_lat) + ',' + str(start_poi_lng),
            'end_point': str(end_poi_lat) + ',' + str(end_poi_lng),
            'distance': best_node.get_total_distance(),
            'time': best_node.cost_minutes,
        }

        if history:
            to_return['history'] = history_list

        if visualisation:
            branch_routes = []
            Node.found_route = True
            # pq.heapify()

            while True:
                if pq.empty():
                    break
                best_branch_node = pq.get()
                branch = {'cost': best_branch_node.cost,
                          'distance': best_branch_node.distance,
                          'total_cost': best_branch_node.calculate_total_cost(),
                          'route': self._route_to_str_(self._get_route_(best_branch_node))}
                branch_routes.append(branch)
                # pq.heapify()

            to_return['branch'] = branch_routes

        logger.info('******************************************************')
        logger.info(f'Total Nodes Searched: {node_count}')
        logger.info(f'Nodes In Route: {len(route)}')
        logger.info(f'Estimated distance: {best_node.get_total_distance():.2f}km')
        logger.info(f'Estimated Time: {best_node.cost_minutes:.2f}m')

        return to_return

    def bi_a_star(self, source_lat, source_lng, target_lat, target_lng, visualisation=False, history=False):
        start_poi_lat, start_poi_lng, start_geom_id, start_on_vertix = self.pg.find_closest_point_on_edge(source_lng, source_lat,
                                                                                              Flags.CAR.value)
        end_poi_lat, end_poi_lng, end_geom_id, end_on_vertix = self.pg.find_closest_point_on_edge(target_lng, target_lat,
                                                                                              Flags.CAR.value)

        source_node = Node(-1, 0, 0, start_poi_lng, start_poi_lat)
        target_node = Node(-1, 0, 0, end_poi_lng, end_poi_lat)

        if start_on_vertix:
            start_nodes = self.pg.get_ways(Node(start_geom_id, 0, 0, 0, 0), target_node, Flags.CAR, (start_geom_id,))
        else:
            start_nodes = self.pg.find_nearest_road(start_poi_lng, start_poi_lat, start_geom_id)

        if end_on_vertix:
            end_nodes = self.pg.get_ways(Node(end_geom_id, 0, 0, 0, 0), source_node, Flags.CAR, (end_geom_id,))
        else:
            end_nodes = self.pg.find_nearest_road(end_poi_lng, end_poi_lat, end_geom_id)

        source_node_dict = {node.node_id: node for node in start_nodes}

        target_node_dict = {node.node_id: node for node in end_nodes}

        source_pq = PriorityQueue()
        for node in start_nodes:
            source_pq.put(node)

        target_pq = PriorityQueue()
        for node in end_nodes:
            target_pq.put(node)

        notify_queue = Queue() # maxsize causing locking, probably race condition

        history_list = [[node.serialize() for node in start_nodes] + [node.serialize() for node in end_nodes]] if history else None

        t0 = time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            source_future = executor.submit(astar_manager, self.pg, source_pq, notify_queue, source_node_dict,
                                            target_node, target_node_dict, Flags.CAR, history_list, 3)
            target_future = executor.submit(astar_manager, self.pg, target_pq, notify_queue, target_node_dict,
                                            source_node, source_node_dict, Flags.CAR, history_list, 3)
            node_count = source_future.result() + target_future.result()
        best_node = notify_queue.get()
        middle_node = notify_queue.get()
        t1 = time()
        logger.info(f'Bidirectional A-Star workers time: {round(t1 - t0, 3)}s')

        if history:
            history_list.append([best_node.serialize()])

        route = self._get_route_(best_node) + self._get_route_(middle_node)

        to_return = {
            'route': self._route_to_str_(route),
            'start_point': str(start_poi_lat) + ',' + str(start_poi_lng),
            'end_point': str(end_poi_lat) + ',' + str(end_poi_lng),
            'distance': best_node.get_total_distance(),
            'time': best_node.cost_minutes,
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
    def find_nearest_road(self, x, y, edge_id):
        return self.pg.find_nearest_road(x, y, edge_id)

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
