import logging

from config import conf

target = __import__("dfosm")

logger = logging.getLogger(target.__name__)


class TestAStar:
    @classmethod
    def setup_class(cls):
        cls.config = conf

    def setup_method(self):
        self.dfosm = target.DFOSM(conf.DBNAME, conf.DBUSER, conf.DBPASSWORD, conf.DBHOST, conf.DBPORT, conf.EDGES_TABLE,
                                 conf.VERTICES_TABLE)

    def teardown_method(self):
        self.dfosm.close_database()

    def test_a_star(self):
        # Lighthouse to Doonbeg
        nodes = self.dfosm.a_star(472893, 420221)
        # Ard na Greine
        # nodes = self.dfosm.a_star(40272, 47713)
        # Tullig to Ballylongford
        # nodes = self.dfosm.a_star(281360, 918311)

        assert nodes is not None

    def test_a_star_incorrect(self):
        nodes = self.dfosm.a_star(238, -1)

        assert nodes is None

    def test_a_star_not_found(self):
        nodes = self.dfosm.a_star(238, 1000000)
        assert nodes is None
