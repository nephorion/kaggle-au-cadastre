import pytest

from cadastre_gnaf.geometry.point_in_ring import point_in_ring

SQUARE = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]
U_SHAPE = [(0, 0), (0, 10), (3, 10), (3, 3), (7, 3), (7, 10), (10, 10), (10, 0), (0, 0)]


@pytest.mark.parametrize(("x", "y", "inside"), [(5, 5, True), (11, 5, False), (-1, -1, False), (9.9, 0.1, True)])
def test_square(x, y, inside):
    assert point_in_ring(x, y, SQUARE) is inside


def test_concave_notch_is_outside():
    assert point_in_ring(5, 6, U_SHAPE) is False
    assert point_in_ring(1, 6, U_SHAPE) is True
