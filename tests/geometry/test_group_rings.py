from cadastre_gnaf.geometry.group_rings import group_rings
from cadastre_gnaf.geometry.signed_area import signed_area

SHELL = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]           # clockwise
HOLE = [(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]                 # counter-clockwise, inside SHELL
SHELL2 = [(20, 0), (20, 1), (21, 1), (21, 0), (20, 0)]
ORPHAN = [(50, 50), (51, 50), (51, 51), (50, 51), (50, 50)]     # counter-clockwise, outside everything


def group(rings):
    return group_rings(rings, [signed_area(r) for r in rings])


def test_hole_assigned_to_containing_shell():
    assert group([SHELL, HOLE]) == [(0, [1])]


def test_separate_shells():
    assert group([SHELL, SHELL2]) == [(0, []), (1, [])]


def test_orphan_hole_becomes_its_own_polygon():
    assert group([SHELL, ORPHAN]) == [(0, []), (1, [])]


def test_all_counter_clockwise_treated_as_shells():
    assert group([HOLE, ORPHAN]) == [(0, []), (1, [])]
