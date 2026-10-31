from cadastre_gnaf.geometry.clean_rings import clean_rings
from cadastre_gnaf.geometry.format_coord import format_coord
from cadastre_gnaf.geometry.group_rings import group_rings
from cadastre_gnaf.geometry.polygon_wkt import polygon_wkt
from cadastre_gnaf.geometry.representative_point import representative_point
from cadastre_gnaf.geometry.signed_area import signed_area


def esri_to_wkt(geom, decimals=6):
    """Return (wkt, point_lon, point_lat) for an Esri JSON polygon/point geometry."""
    if not geom:
        return "", None, None
    if "x" in geom and "y" in geom:
        if geom["x"] is None:
            return "", None, None
        wkt = f"POINT ({format_coord(geom['x'], decimals)} {format_coord(geom['y'], decimals)})"
        return wkt, geom["x"], geom["y"]
    rings = clean_rings(geom.get("rings"))
    if not rings:
        return "", None, None
    areas = [signed_area(r) for r in rings]
    parts = group_rings(rings, areas)
    wkt = polygon_wkt(rings, parts, decimals)
    # representative point of the largest part
    s, hs = max(parts, key=lambda p: abs(areas[p[0]]))
    cx, cy = representative_point(rings[s], [rings[h] for h in hs])
    return wkt, round(cx, decimals + 1), round(cy, decimals + 1)
