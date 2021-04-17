import logging

import pytest

from .config import conf

target = __import__("dfosm")

logger = logging.getLogger(target.__name__)
logger.setLevel(logging.INFO)


class TestKnownRoutes:
    known_routes_short = [
        {'start_name': 'Tullig', 'end_name': 'Kilrush', 'start_lat': 52.614722, 'start_lng': -9.776111,
         'end_lat': 52.6397222, 'end_lng': -9.4833283, 'target_time': 21, 'target_distance': 27},
        {'start_name': 'Tullig', 'end_name': 'Ennis', 'start_lat': 52.614722, 'start_lng': -9.776111,
         'end_lat': 52.8435152, 'end_lng': -8.983747, 'target_time': 48, 'target_distance': 69},
        {'start_name': 'Ard Na Greine', 'end_name': 'Ard Na Greine', 'start_lat': 52.7082188, 'start_lng': -8.8685024,
         'end_lat': 52.8397697, 'end_lng': -8.9796499, 'target_time': 14, 'target_distance': 21},
    ]

    known_routes_long = [
        {'start_name': 'Limerick', 'end_name': 'Cork', 'start_lat': 52.6593646, 'start_lng': -8.62311436,
         'end_lat': 51.89864135, 'end_lng': -8.51376165, 'target_time': 69, 'target_distance': 101},
        {'start_name': 'Limerick', 'end_name': 'Maynooth', 'start_lat': 52.6593646, 'start_lng': -8.62311436,
         'end_lat': 53.38553995, 'end_lng': -6.59743538, 'target_time': 132, 'target_distance': 214}
    ]

    @classmethod
    def setup_class(cls):
        cls.config = conf

    def setup_method(self):
        self.dfosm = target.DFOSM(6, 120, conf.DBNAME, conf.DBUSER, conf.DBPASSWORD, conf.DBHOST, conf.DBPORT,
                                  conf.EDGES_TABLE, conf.VERTICES_TABLE)

    def teardown_method(self):
        self.dfosm.close_database()

    @pytest.mark.parametrize('known_route', known_routes_short)
    def test_dijkstra(self, known_route):
        logger.info(
            f'Testing dijkstra between {known_route["start_name"]} and {known_route["end_name"]}. '
            f'Expecting {known_route["target_time"]} mins and {known_route["target_distance"]} km.')
        result = self.dfosm.dijkstra(known_route['start_lat'], known_route['start_lng'], known_route['end_lat'],
                                     known_route['end_lng'], target.Flags.CAR.value)

        assert result['route'] is not None
        assert result['time'] <= known_route['target_time']
        assert result['distance'] <= known_route['target_distance']

    @pytest.mark.parametrize('known_route', known_routes_short)
    def test_bi_dijkstra(self, known_route):
        logger.info(
            f'Testing bi-dijkstra between {known_route["start_name"]} and {known_route["end_name"]}. '
            f'Expecting {known_route["target_time"]} mins and {known_route["target_distance"]} km.')
        result = self.dfosm.bi_dijkstra(known_route['start_lat'], known_route['start_lng'], known_route['end_lat'],
                                        known_route['end_lng'], target.Flags.CAR.value)

        assert result['route'] is not None
        assert result['time'] <= known_route['target_time']
        assert result['distance'] <= known_route['target_distance']

    @pytest.mark.parametrize('known_route', known_routes_short + known_routes_long)
    def test_a_star(self, known_route):
        logger.info(
            f'Testing A-Star between {known_route["start_name"]} and {known_route["end_name"]}. '
            f'Expecting {known_route["target_time"]} mins and {known_route["target_distance"]} km.')
        result = self.dfosm.a_star(known_route['start_lat'], known_route['start_lng'], known_route['end_lat'],
                                   known_route['end_lng'], target.Flags.CAR.value)

        assert result['route'] is not None
        assert result['time'] <= known_route['target_time']
        assert result['distance'] <= known_route['target_distance']

    @pytest.mark.parametrize('known_route', known_routes_short + known_routes_long)
    def test_bi_a_star(self, known_route):
        logger.info(
            f'Testing bi-A-Star between {known_route["start_name"]} and {known_route["end_name"]}. '
            f'Expecting {known_route["target_time"]} mins and {known_route["target_distance"]} km.')
        result = self.dfosm.bi_a_star(known_route['start_lat'], known_route['start_lng'], known_route['end_lat'],
                                      known_route['end_lng'], target.Flags.CAR.value)

        assert result['route'] is not None
        assert result['time'] <= known_route['target_time']
        assert result['distance'] <= known_route['target_distance']
