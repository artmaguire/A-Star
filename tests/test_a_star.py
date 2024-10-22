import logging

from .config import conf

target = __import__("dfosm")

logger = logging.getLogger(target.__name__)
logger.setLevel(logging.INFO)


class TestAStar:
    @classmethod
    def setup_class(cls):
        cls.config = conf

    def setup_method(self):
        self.dfosm = target.DFOSM(6, 120, conf.DBNAME, conf.DBUSER, conf.DBPASSWORD, conf.DBHOST, conf.DBPORT,
                                  conf.EDGES_TABLE, conf.VERTICES_TABLE)

    def teardown_method(self):
        self.dfosm.close_database()

    def test_dijkstra(self):
        # Lighthouse to Doonbeg
        # geojson = self.dfosm.a_star(52.614722,-9.776111,52.5595239,-9.9381113, visualisation=False)
        # Ard na Greine
        geojson = self.dfosm.dijkstra(52.614722, -9.776111, 52.8435152, -8.983747, target.Flags.CAR.value,
                                      history=False)
        # Tullig to Ballylongford
        # geojson = self.dfosm.a_star(281360, 918311)
        # Tullig to Kilrush Marina
        # geojson = self.dfosm.a_star(52.614722, -9.776111, 52.63387335, -9.49417737)

        logger.info(geojson)

        assert geojson is not None

    def test_bi_dijkstra(self):
        # Lighthouse to Doonbeg
        # geojson = self.dfosm.a_star(52.614722,-9.776111,52.5595239,-9.9381113, visualisation=False)
        # Ard na Greine
        geojson = self.dfosm.bi_dijkstra(52.7082188, -8.8685024, 52.8397697, -8.9796499, target.Flags.BIKE.value)

        logger.info(geojson)

        assert geojson is not None

    def test_a_star(self):
        # Lighthouse to Doonbeg
        # geojson = self.dfosm.a_star(52.614722,-9.776111,52.5595239,-9.9381113, visualisation=False)
        # Ard na Greine
        # geojson = self.dfosm.a_star(52.61638, -9.78134, 52.637107, -9.486786, target.Flags.CAR.value,
        #                             history=False)
        geojson = self.dfosm.a_star(53.34980185, -6.26025419, 53.4230832, -7.942705, target.Flags.CAR.value,
                                    history=False)
        # Tullig to Ballylongford
        # geojson = self.dfosm.a_star(281360, 918311)
        # Tullig to Kilrush Marina
        # geojson = self.dfosm.a_star(52.614722, -9.776111, 52.63387335, -9.49417737)

        logger.info(geojson)

        assert geojson is not None

    def test_bi_a_star(self):
        # Lighthouse to Doonbeg
        geojson = self.dfosm.a_star(52.614722, -9.776111, 52.5595239, -9.9381113, visualisation=False)
        # Ard na Greine
        # geojson = self.dfosm.bi_a_star(52.7082188, -8.8685024, 52.8397697, -8.9796499)

        logger.info(geojson)

        assert geojson is not None

    def test_all_roads(self):
        geojson = self.dfosm.all_roads(53.3183424, -6.3682900, 1, 3600, history=True)
        logger.info(geojson)

        assert geojson is not None

    def test_a_star_incorrect(self):
        geojson = self.dfosm.a_star(238, -1)

        assert geojson is None

    def test_a_star_not_found(self):
        geojson = self.dfosm.a_star(238, 1000000000)
        assert geojson is None

    def test_find_nearest_road(self):
        node1, node2 = self.dfosm.find_nearest_road(-9.784956, 52.616494)
        logger.info(node1)
        logger.info(node2)

        assert node1 is not None and node2 is not None
