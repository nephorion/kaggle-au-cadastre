from cadastre_gnaf.geometry.point_in_ring import point_in_ring


def group_rings(rings, areas):
    """Assign holes to shells -> [(shell_index, [hole_index, ...]), ...]."""
    shells = [i for i, a in enumerate(areas) if a < 0]       # Esri: outer rings are clockwise
    holes = [i for i, a in enumerate(areas) if a >= 0]
    if not shells:                                          # non-standard orientation: treat all as shells
        shells, holes = list(range(len(rings))), []
    polys = {i: [] for i in shells}
    for h in holes:
        hx, hy = rings[h][0]
        owner = next((s for s in shells if point_in_ring(hx, hy, rings[s])), None)
        if owner is None:                                   # orphan hole -> its own polygon
            polys[h] = []
        else:
            polys[owner].append(h)
    return list(polys.items())
