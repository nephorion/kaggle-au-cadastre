from cadastre_gnaf.geometry.to_local import to_local


def signed_area(ring):
    """Shoelace area of a closed ring: negative = clockwise (Esri outer ring)."""
    r, _, _ = to_local(ring)
    s = 0.0
    for (x1, y1), (x2, y2) in zip(r, r[1:]):
        s += x1 * y2 - x2 * y1
    return s / 2.0
