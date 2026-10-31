def format_coord(v, decimals):
    """Fixed-point number with trailing zeros removed."""
    s = f"{v:.{decimals}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s
