def parse_state_pairs(pairs):
    """['sa=/x.shp', 'NT=y'] -> {'SA': '/x.shp', 'NT': 'y'}."""
    out = {}
    for kv in pairs:
        if "=" not in kv:
            raise ValueError(f"expected STATE=VALUE, got {kv!r}")
        state, value = kv.split("=", 1)
        out[state.strip().upper()] = value
    return out
