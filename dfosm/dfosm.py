import logging
from time import time

from .classes import PriorityQueue
from .classes import Node
from .utilities import Flags
from .utilities import PGHelper

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
        self.pg.close_connection()

    def a_star(self, source_lat, source_lng, target_lat, target_lng, visualisation=False, history=False):
        pq = PriorityQueue()

        best_node, second_best_node = self.pg.find_nearest_road(source_lng, source_lat)

        target_node = Node(-1, 0, 0, target_lng, target_lat)

        target_node_a, target_node_b = self.pg.find_nearest_road(target_lng, target_lat)

        closed_set = [best_node.node_id, second_best_node.node_id]
        pq.push(second_best_node)

        history_list = [[best_node.serialize(), second_best_node.serialize()]]

        node_count = 1

        while True:
            # t0 = time()
            nodes = self.pg.get_ways(best_node, target_node, Flags.CAR, tuple(closed_set))
            # TODO: Check if node is the target instead of waiting until it gets popped from PriorityQueue
            if history:
                history_list.append([node.serialize() for node in nodes])
            # t1 = time()
            pq.push_many(nodes)

            best_node = pq.pop()
            logger.debug(best_node.__str__())

            closed_set.append(best_node.node_id)

            # print(f'Count: {node_count}\t\tDB: {round((t1 - t0) * 1000000)}')

            if best_node.node_id == target_node_a.node_id:
                target_node.geojson = target_node_a.geojson
                break
            elif best_node.node_id == target_node_b.node_id:
                target_node.geojson = target_node_b.geojson
                break

            node_count += 1

        target_node.previous = best_node
        best_node = target_node

        if history:
            history_list.append([best_node.serialize()])

        curr_node = best_node
        route = self._get_route_(curr_node)

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
            pq.heapify()

            best_branch_node = pq.pop()

            while best_branch_node:
                branch = {'cost': best_branch_node.cost,
                          'distance': best_branch_node.distance,
                          'total_cost': best_branch_node.calculate_total_cost(),
                          'route': self._route_to_str_(self._get_route_(best_branch_node))}
                branch_routes.append(branch)
                pq.heapify()

                best_branch_node = pq.pop()

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
    def _get_route_(node):
        route = []
        while node and node.geojson:
            route.append(node.geojson)
            node = node.get_previous()

        route.reverse()
        return route

    @staticmethod
    def _route_to_str_(route):
        return '[' + ','.join(route) + ']'
