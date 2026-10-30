from cadastre_gnaf.geometry.to_local import to_local


def ring_centroid(ring, area):
    """Area centroid of a closed ring (vertex mean for degenerate rings)."""
    if area == 0:
        xs, ys = zip(*ring)
        return sum(xs) / len(xs), sum(ys) / len(ys)
    r, x0, y0 = to_local(ring)
    cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(r, r[1:]):
        f = x1 * y2 - x2 * y1
        cx += (x1 + x2) * f
        cy += (y1 + y2) * f
    return x0 + cx / (6 * area), y0 + cy / (6 * area)
