from cadastre_gnaf.geometry.ring_wkt import ring_wkt


def test_ring_wkt():
    assert ring_wkt([(0.0, 0.0), (1.5, 2.0), (0.0, 0.0)], 6) == "(0 0,1.5 2,0 0)"


def test_rounds_to_decimals():
    assert ring_wkt([(1.23456, 2.0)], 2) == "(1.23 2)"
