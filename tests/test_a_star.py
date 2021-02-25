from a_star import a_star
from tag_check import get_tag_tuple

import logging

logger = logging.getLogger(__name__)

def test_a_star():
    # 238 Source: Tynwald Close
    # 496 Target: Reayrt Aalin
    # nodes = a_star(76, 496)
    # nodes = a_star(1867, 239)
    # nodes = a_star(8, 57)
    # nodes = a_star(55, 48)
    # Ard na Greine
    nodes = a_star(75107, 68650)

    assert nodes is not None


def test_a_star_incorrect():
    nodes = a_star(238, -1)

    assert nodes is None


def test_a_star_not_found():
    nodes = a_star(238, 1000000)
    assert nodes is None

def test_tag_car():
    tag_tuple = get_tag_tuple('car')
    logger.debug(str(tag_tuple))

    assert type(tag_tuple) is tuple


def test_tag_missing():
    tag_tuple = get_tag_tuple('not_tag')

    assert tag_tuple is None

def test_tag_none():
    tag_str = get_tag_tuple([])

    assert tag_str is None
