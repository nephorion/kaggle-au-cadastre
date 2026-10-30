from cadastre_gnaf.geometry.point_in_ring import point_in_ring
from cadastre_gnaf.geometry.ring_centroid import ring_centroid
from cadastre_gnaf.geometry.scanline_point import scanline_point
from cadastre_gnaf.geometry.signed_area import signed_area


def representative_point(shell, holes):
    """Centroid of the shell if it falls inside the polygon, else a scanline point."""
    cx, cy = ring_centroid(shell, signed_area(shell))
    if point_in_ring(cx, cy, shell) and not any(point_in_ring(cx, cy, h) for h in holes):
        return cx, cy
    return scanline_point(shell, holes)
