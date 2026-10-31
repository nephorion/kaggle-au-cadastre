import re


def norm_key(s):
    """Normalise a parcel key for comparison: upper-case, no whitespace."""
    if s is None:
        return None
    s = re.sub(r"\s+", "", str(s)).upper()
    return s or None
