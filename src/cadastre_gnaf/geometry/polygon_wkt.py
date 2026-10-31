from cadastre_gnaf.geometry.ring_wkt import ring_wkt


def polygon_wkt(rings, parts, decimals):
    """POLYGON or MULTIPOLYGON WKT from rings grouped as [(shell, [holes])]."""
    parts_wkt = ["(" + ",".join(ring_wkt(rings[i], decimals) for i in [s] + hs) + ")" for s, hs in parts]
    if len(parts_wkt) == 1:
        return "POLYGON " + parts_wkt[0]
    return "MULTIPOLYGON (" + ",".join(parts_wkt) + ")"
