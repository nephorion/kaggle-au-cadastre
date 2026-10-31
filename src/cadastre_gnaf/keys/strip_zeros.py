def strip_zeros(s):
    """Drop leading zeros, keeping a single '0' for all-zero input."""
    return s.lstrip("0") or ("0" if s else "")
