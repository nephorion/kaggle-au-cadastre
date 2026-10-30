def clean_rings(raw_rings):
    """Esri ring lists -> closed rings of float tuples, dropping degenerate ones."""
    rings = []
    for r in raw_rings or []:
        r = [(float(p[0]), float(p[1])) for p in r if p is not None and len(p) >= 2]
        if len(r) < 3:
            continue
        if r[0] != r[-1]:
            r.append(r[0])
        if len(r) >= 4:
            rings.append(r)
    return rings
