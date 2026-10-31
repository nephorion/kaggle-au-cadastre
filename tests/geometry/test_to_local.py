from cadastre_gnaf.geometry.to_local import to_local


def test_shifts_to_first_vertex():
    ring, x0, y0 = to_local([(150.0, -33.0), (151.0, -33.0), (150.0, -32.0)])
    assert (x0, y0) == (150.0, -33.0)
    assert ring == [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
