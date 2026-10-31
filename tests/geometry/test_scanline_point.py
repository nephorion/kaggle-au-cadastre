from cadastre_gnaf.geometry.point_in_ring import point_in_ring
from cadastre_gnaf.geometry.scanline_point import scanline_point

SQUARE = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]


def test_square_midpoint():
    assert scanline_point(SQUARE, []) == (5.0, 5.0)


def test_avoids_hole_and_picks_widest_span():
    hole = [(2, 2), (2, 8), (4, 8), (4, 2), (2, 2)]
    x, y = scanline_point(SQUARE, [hole])
    assert y == 5.0 and x == 7.0                     # spans [0,2] and [4,10] -> widest is [4,10]
    assert not point_in_ring(x, y, hole)


def test_degenerate_shell_returns_first_vertex():
    flat = [(0, 0), (5, 0), (10, 0), (0, 0)]
    assert scanline_point(flat, []) == (0, 0)
