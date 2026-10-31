import pytest

from cadastre_gnaf.geometry.point_in_ring import point_in_ring
from cadastre_gnaf.geometry.representative_point import representative_point

SQUARE = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]


def test_uses_centroid_when_inside():
    assert representative_point(SQUARE, []) == pytest.approx((5.0, 5.0))


def test_avoids_hole_over_centroid():
    hole = [(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]
    x, y = representative_point(SQUARE, [hole])
    assert point_in_ring(x, y, SQUARE) and not point_in_ring(x, y, hole)


def test_concave_shape_with_centroid_outside():
    c_shape = [(0, 0), (0, 10), (10, 10), (10, 9), (1, 9), (1, 1), (10, 1), (10, 0), (0, 0)]
    x, y = representative_point(c_shape, [])
    assert point_in_ring(x, y, c_shape)
