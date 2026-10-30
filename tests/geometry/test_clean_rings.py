from cadastre_gnaf.geometry.clean_rings import clean_rings


def test_closes_open_rings_and_converts_to_float_tuples():
    assert clean_rings([[[0, 0], [0, 1], [1, 1]]]) == [[(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (0.0, 0.0)]]


def test_keeps_closed_rings():
    ring = [[0, 0], [0, 1], [1, 1], [0, 0]]
    assert clean_rings([ring]) == [[(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (0.0, 0.0)]]


def test_drops_bad_points_and_degenerate_rings():
    assert clean_rings([[[0, 0], None, [1], [1, 1]]]) == []          # only 2 valid points
    assert clean_rings([[[0, 0], [1, 1], [0, 0]]]) == []            # closed but only 3 vertices


def test_extra_ordinates_ignored():
    assert clean_rings([[[0, 0, 5], [0, 1, 5], [1, 1, 5]]])[0][1] == (0.0, 1.0)


def test_none_input():
    assert clean_rings(None) == []
