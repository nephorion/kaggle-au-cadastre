from cadastre_gnaf.geometry.format_coord import format_coord


def ring_wkt(ring, decimals):
    return "(" + ",".join(f"{format_coord(x, decimals)} {format_coord(y, decimals)}" for x, y in ring) + ")"
