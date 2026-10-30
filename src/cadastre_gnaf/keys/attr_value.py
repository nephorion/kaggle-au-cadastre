import math


def attr_value(attrs, *names):
    """Case-insensitive attribute lookup -> clean string ('' if missing)."""
    for n in names:
        for k in (n, n.lower(), n.upper()):
            if k in attrs and attrs[k] is not None:
                v = attrs[k]
                if isinstance(v, float):
                    if math.isnan(v):
                        return ""
                    if v.is_integer():
                        v = int(v)
                s = str(v).strip()
                if s.lower() in ("", "none", "null", "nan"):
                    return ""
                return s
    return ""
