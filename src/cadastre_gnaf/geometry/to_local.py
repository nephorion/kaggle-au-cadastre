def to_local(ring):
    """Shift a ring to its first vertex: avoids float cancellation at lon ~150."""
    x0, y0 = ring[0]
    return [(x - x0, y - y0) for x, y in ring], x0, y0
