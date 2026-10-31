def scanline_point(shell, holes):
    """Point inside polygon: midpoint of the widest interior span on the line through the bbox middle."""
    ys = [p[1] for p in shell]
    y = (min(ys) + max(ys)) / 2.0
    xs = []
    for ring in [shell] + holes:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            if (y1 > y) != (y2 > y):
                xs.append((x2 - x1) * (y - y1) / (y2 - y1) + x1)
    xs.sort()
    best = None
    for a, b in zip(xs[0::2], xs[1::2]):
        if best is None or (b - a) > (best[1] - best[0]):
            best = (a, b)
    if best is None:
        return shell[0]
    return (best[0] + best[1]) / 2.0, y
