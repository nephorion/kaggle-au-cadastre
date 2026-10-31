from cadastre_gnaf.geometry.polygon_wkt import polygon_wkt

A = [(0, 0), (0, 1), (1, 1), (0, 0)]
B = [(5, 5), (5, 6), (6, 6), (5, 5)]


def test_single_part_is_polygon():
    assert polygon_wkt([A], [(0, [])], 6) == "POLYGON ((0 0,0 1,1 1,0 0))"


def test_polygon_with_hole():
    assert polygon_wkt([A, B], [(0, [1])], 6) == "POLYGON ((0 0,0 1,1 1,0 0),(5 5,5 6,6 6,5 5))"


def test_multiple_parts_is_multipolygon():
    assert polygon_wkt([A, B], [(0, []), (1, [])], 6) == \
        "MULTIPOLYGON (((0 0,0 1,1 1,0 0)),((5 5,5 6,6 6,5 5)))"
