from a_star import a_star
from tag_check import get_tag_tuple

import logging

logger = logging.getLogger(__name__)

def test_a_star():
    # Lighthouse to Doonbeg
    nodes = a_star(420221, 472893)

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
