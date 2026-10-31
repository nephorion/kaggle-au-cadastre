import pytest

from cadastre_gnaf.geometry.signed_area import signed_area

CW = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]


def test_clockwise_is_negative():
    assert signed_area(CW) == -4.0


def test_counter_clockwise_is_positive():
    assert signed_area(CW[::-1]) == 4.0


def test_degenerate_ring_has_zero_area():
    assert signed_area([(0, 0), (1, 1), (2, 2), (0, 0)]) == 0.0


def test_precise_at_real_longitudes():
    ring = [(151.2001, -33.8), (151.2001, -33.799), (151.2011, -33.799), (151.2011, -33.8), (151.2001, -33.8)]
    assert signed_area(ring) == pytest.approx(-1e-6, rel=1e-6)
