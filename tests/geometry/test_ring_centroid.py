import pytest

from cadastre_gnaf.geometry.ring_centroid import ring_centroid
from cadastre_gnaf.geometry.signed_area import signed_area


def test_square_centroid():
    ring = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    assert ring_centroid(ring, signed_area(ring)) == pytest.approx((1.0, 1.0))


def test_triangle_centroid():
    ring = [(0, 0), (3, 0), (0, 3), (0, 0)]
    assert ring_centroid(ring, signed_area(ring)) == pytest.approx((1.0, 1.0))


def test_zero_area_falls_back_to_vertex_mean():
    ring = [(0, 0), (2, 2), (0, 0)]
    assert ring_centroid(ring, 0) == pytest.approx((2 / 3, 2 / 3))


def test_exact_at_real_coordinates():
    ring = [(151.2001, -33.8), (151.2001, -33.799), (151.2011, -33.799), (151.2011, -33.8), (151.2001, -33.8)]
    cx, cy = ring_centroid(ring, signed_area(ring))
    assert abs(cx - 151.2006) < 1e-9 and abs(cy + 33.7995) < 1e-9
