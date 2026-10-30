from cadastre_gnaf.geometry import esri_to_wkt


def test_square_with_hole():
    w, x, y = esri_to_wkt({"rings": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
                                     [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]]})
    assert w.startswith("POLYGON ((0 0,0 10") and "(4 4,6 4" in w
    assert not (4 < x < 6 and 4 < y < 6)                # point avoids the hole


def test_centroid_exact_at_real_coordinates():
    _, x, y = esri_to_wkt({"rings": [[[151.2001, -33.8], [151.2001, -33.799], [151.2011, -33.799],
                                      [151.2011, -33.8], [151.2001, -33.8]]]})
    assert abs(x - 151.2006) < 1e-9 and abs(y + 33.7995) < 1e-9


def test_two_shells_is_multipolygon():
    w, _, _ = esri_to_wkt({"rings": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
                                     [[5, 5], [5, 6], [6, 6], [6, 5], [5, 5]]]})
    assert w.startswith("MULTIPOLYGON")


def test_point_taken_from_largest_part():
    _, x, y = esri_to_wkt({"rings": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
                                     [[10, 10], [10, 20], [20, 20], [20, 10], [10, 10]]]})
    assert (x, y) == (15.0, 15.0)


def test_point_geometry():
    assert esri_to_wkt({"x": 149.1, "y": -35.3}) == ("POINT (149.1 -35.3)", 149.1, -35.3)


def test_null_point():
    assert esri_to_wkt({"x": None, "y": None}) == ("", None, None)


def test_empty_inputs():
    assert esri_to_wkt(None) == ("", None, None)
    assert esri_to_wkt({}) == ("", None, None)
    assert esri_to_wkt({"rings": [[[0, 0], [1, 1]]]}) == ("", None, None)


def test_point_rounded_to_decimals_plus_one():
    _, x, _ = esri_to_wkt({"rings": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}, decimals=2)
    assert x == 0.5
    _, x, _ = esri_to_wkt({"rings": [[[0, 0], [0, 1], [1 / 3, 1], [1 / 3, 0], [0, 0]]]}, decimals=2)
    assert x == 0.167
