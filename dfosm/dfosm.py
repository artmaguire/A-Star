import concurrent.futures
import logging
# from .classes import PriorityQueue
from queue import PriorityQueue, Queue

import math
from time import time

from .classes import AStarManager
from .classes import Node
from .classes import NodeOptions
from .classes import PGHelper
from .classes import all_roads_worker
from .utilities import Flags
from .utilities import get_distance
from .weighting import WeighterFactory

logger = logging.getLogger(__name__.split(".")[0])


class DFOSM:
    def __init__(self, threads=2, timeout=120, dbname='postgres', dbuser='postgres', dbpassword='postgres',
                 dbhost='127.0.0.1', dbport=5432, edges_table='edges',
                 vertices_table='vertices'):
        self.threads = threads
        self.timeout = timeout
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
        self.pg.close_all_connections()

    def dijkstra(self, source_lat, source_lng, target_lat, target_lng, flag=Flags.CAR.value, visualisation=False,
                 history=False):
        flag = Flags.CAR.value if flag < 0 else flag
        node_options = NodeOptions(dijkstra=True)

        return self.__a_star__(source_lat, source_lng, target_lat, target_lng, flag=flag, visualisation=visualisation,
                               history=history,
                               bidirectional=False,
                               node_options=node_options)

    def bi_dijkstra(self, source_lat, source_lng, target_lat, target_lng, flag=Flags.CAR.value, visualisation=False,
                    history=False):
        flag = Flags.CAR.value if flag < 0 else flag
        node_options = NodeOptions(dijkstra=True)

        return self.__a_star__(source_lat, source_lng, target_lat, target_lng, flag=flag, visualisation=visualisation,
                               history=history,
                               bidirectional=True,
                               node_options=node_options)

    def a_star(self, source_lat, source_lng, target_lat, target_lng, flag=Flags.CAR.value, visualisation=False,
               history=False):
        flag = Flags.CAR.value if flag < 0 else flag
        weighter = WeighterFactory.create_weighter(flag)
        node_options = NodeOptions(weighter=weighter)

        return self.__a_star__(source_lat, source_lng, target_lat, target_lng, flag=flag, visualisation=visualisation,
                               history=history,
                               bidirectional=False,
                               node_options=node_options)

    def bi_a_star(self, source_lat, source_lng, target_lat, target_lng, flag=Flags.CAR.value, visualisation=False,
                  history=False):
        flag = Flags.CAR.value if flag < 0 else flag
        weighter = WeighterFactory.create_weighter(flag)
        node_options = NodeOptions(weighter=weighter)

        return self.__a_star__(source_lat, source_lng, target_lat, target_lng, flag=flag, visualisation=visualisation,
                               history=history,
                               bidirectional=True,
                               node_options=node_options)

    def __a_star__(self, source_lat, source_lng, target_lat, target_lng, flag=Flags.CAR.value, visualisation=False,
                   history=False,
                   bidirectional=True, node_options=NodeOptions()):
        start_poi_lat, start_poi_lng, start_edge_id, start_on_vertix = \
            self.pg.find_closest_point_on_edge(source_lng, source_lat, flag)
        end_poi_lat, end_poi_lng, end_edge_id, end_on_vertix = \
            self.pg.find_closest_point_on_edge(target_lng, target_lat, flag)

        node_options.starting_distance = get_distance(start_poi_lat, start_poi_lng, end_poi_lat, end_poi_lng)

        source_node = Node(lng=start_poi_lng, lat=start_poi_lat)
        target_node = Node(lng=end_poi_lng, lat=end_poi_lat)

        if start_on_vertix:
            start_nodes = [Node(node_id=start_edge_id)]
            source_node_dict = {start_nodes[0].node_id: {'node': start_nodes[0], 'neighbours': [start_nodes[0].node_id]}}
        else:
            start_nodes = self.pg.find_nearest_road(start_poi_lng, start_poi_lat, start_edge_id)
            source_node_dict = {
                start_nodes[0].node_id: {'node': start_nodes[0], 'neighbours': [start_nodes[1].node_id]},
                start_nodes[1].node_id: {'node': start_nodes[1], 'neighbours': [start_nodes[0].node_id]}
            }

        if end_on_vertix:
            end_nodes = [Node(node_id=end_edge_id)]
            target_node_dict = {end_nodes[0].node_id: {'node': end_nodes[0], 'neighbours': [end_nodes[0].node_id]}}
        else:
            end_nodes = self.pg.find_nearest_road(end_poi_lng, end_poi_lat, end_edge_id)
            target_node_dict = {
                end_nodes[0].node_id: {'node': end_nodes[0], 'neighbours': [end_nodes[1].node_id]},
                end_nodes[1].node_id: {'node': end_nodes[1], 'neighbours': [end_nodes[0].node_id]}
            }

        source_pq = PriorityQueue()
        for node in start_nodes:
            source_pq.put(node)

        target_pq = PriorityQueue()
        for node in end_nodes:
            target_pq.put(node)

        notify_queue = Queue()  # maxsize causing locking, probably race condition

        history_list = [
            [node.serialize() for node in start_nodes] + [node.serialize() for node in end_nodes]] if history else None

        source_threads = math.ceil(self.threads / 2) if bidirectional else self.threads
        source_manager = AStarManager('S', self.pg, source_pq, notify_queue, source_node_dict,
                                      target_node_dict, target_node, flag, history_list,
                                      source_threads, node_options)
        target_manager = AStarManager('T', self.pg, target_pq, notify_queue, target_node_dict,
                                      source_node_dict, source_node, flag, history_list,
                                      self.threads - source_threads, node_options, reverse_direction=True)

        logger.debug(f'Using {source_threads} source threads, and {self.threads - source_threads} target threads')

        t0 = time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            source_future = executor.submit(source_manager.run)
            target_future = executor.submit(target_manager.run)
            try:
                node_count = source_future.result(timeout=self.timeout) + target_future.result(timeout=self.timeout)
            except concurrent.futures.TimeoutError:
                logger.error(f'Timeout occurred when trying to calculate route with {self.threads} threads.')
                notify_queue.put({})
                return {
                    'error': {
                        'code': -1,
                        'message': 'Timeout when finding route'
                    }
                }
        logger.info(f'{notify_queue.qsize()} potential route(s) found.')

        result = {}

        while not notify_queue.empty():
            r = notify_queue.get()
            if not result:
                result = r
            if r[0].get_cost_minutes() + r[1].get_cost_minutes() < result[0].get_cost_minutes() +\
                    result[1].get_cost_minutes():
                result = r

        best_node = result[0]
        middle_node = result[1]
        t1 = time()
        logger.info(f'A-Star workers time: {round(t1 - t0, 3)}s')

        route = self._get_route_(best_node) + self._get_route_(middle_node)

        to_return = {
            'route': route,
            'source_point': {"lat": source_lat, "lng": source_lng},
            'target_point': {"lat": target_lat, "lng": target_lng},
            'start_point': {"lat": start_poi_lat, "lng": start_poi_lng},
            'end_point': {"lat": end_poi_lat, "lng": end_poi_lng},
            'distance': best_node.get_total_distance() + middle_node.get_total_distance(),
            'time': best_node.get_cost_minutes() + middle_node.get_cost_minutes(),
        }

        if history:
            history_list.append([best_node.serialize()])
            to_return['history'] = history_list

        if visualisation:
            to_return['branch'] = self._get_visualisation_(source_pq) + self._get_visualisation_(target_pq)

        logger.info('******************************************************')
        logger.info(f'Total Nodes Searched: {node_count}')
        logger.info(f'Nodes In Route: {len(route)}')
        logger.info(f'Estimated distance: {best_node.get_total_distance() + middle_node.get_total_distance():.2f}km')
        logger.info(f'Estimated Time: {best_node.get_cost_minutes() + middle_node.get_cost_minutes():.2f}m')

        return to_return

    def all_roads(self, source_lat, source_lng, flag=Flags.CAR.value, timeout=3600, history=False,
                  node_options=NodeOptions()):
        start_poi_lat, start_poi_lng, start_geom_id, start_on_vertix = \
            self.pg.find_closest_point_on_edge(source_lng, source_lat, flag)

        node_options.starting_distance = 0
        node_options.dijkstra = True

        source_node = Node(lng=start_poi_lng, lat=start_poi_lat)

        if start_on_vertix:
            start_nodes = self.pg.get_ways(Node(node_id=start_geom_id), source_node, flag, (start_geom_id,),
                                           node_options, False)
        else:
            start_nodes = self.pg.find_nearest_road(start_poi_lng, start_poi_lat, start_geom_id)

        source_node_dict = {node.node_id: node for node in start_nodes}

        pq = PriorityQueue()
        end_nodes_pq = PriorityQueue()
        for node in start_nodes:
            pq.put(node)

        history_list = [
            [node.serialize() for node in start_nodes]] if history else None

        t0 = time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                all_roads_worker, self.pg, pq, end_nodes_pq, source_node_dict, source_node, flag, history_list,
                node_options, 32) for _ in range(self.threads)]
            try:
                node_count = sum(f.result() for f in futures)
            except concurrent.futures.TimeoutError:
                logger.error(f'Timeout occurred when trying to calculate route with {self.threads} threads.')
                return {
                    'error': {
                        'code': -1,
                        'message': 'Timeout when finding route'
                    }
                }

        t1 = time()
        logger.info(f'A-Star workers time: {round(t1 - t0, 3)}s')

        to_return = {'start_point': {"lat": start_poi_lat, "lng": start_poi_lng}, 'branch': self._get_visualisation_(
            end_nodes_pq)}

        all_roads_geojson = {"type": "FeatureCollection", "features": []}

        for b in to_return['branch']:
            for route in b['route']:
                all_roads_geojson['features'].append({"type": "Feature", "properties": {}, "geometry": route})

        # print(all_roads_geojson)

        with open('../all_roads/all_roads.json', 'w') as f:
            f.write(str(all_roads_geojson))

        # if history:
        #     history_list.append([best_node.serialize()])
        #     to_return['history'] = history_list

        logger.info('******************************************************')
        logger.info(f'Total Nodes Searched: {node_count}')

        return to_return

    # X: longitude, Y: latitude

    def find_nearest_road(self, x, y, edge_id):
        return self.pg.find_nearest_road(x, y, edge_id)

    def _get_visualisation_(self, pq):
        branch_routes = []

        while True:
            if pq.empty():
                break
            best_branch_node = pq.get()
            branch = {'cost': best_branch_node.cost,
                      'distance': best_branch_node.distance,
                      'total_cost': best_branch_node.calculate_total_cost(),
                      'route': self._get_route_(best_branch_node)}
            branch_routes.append(branch)

        return branch_routes

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
