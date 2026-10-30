from cadastre_gnaf.keys.norm_key import norm_key


def join_key(*parts, required=None):
    """Join parts with '/'. `required` = indexes that must be non-empty."""
    required = range(len(parts)) if required is None else required
    if any(not parts[i] for i in required):
        return None
    return norm_key("/".join(parts))
