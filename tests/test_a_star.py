from a_star import a_star


def test_a_star():
    # 238 Source: Tynwald Close
    # 496 Target: Reayrt Aalin
    nodes = a_star(238, 496)

    assert nodes is not None


def test_a_star_incorrect():
    nodes = a_star(238, -1)

    assert nodes is None


def test_a_star_not_found():
    nodes = a_star(238, 1000000)
    assert nodes is None
