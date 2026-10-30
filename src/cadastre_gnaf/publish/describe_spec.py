MAX_INLINE_CODES = 4


def describe_spec(spec, name=lambda c: c):
    """Human-readable Markdown for a FIELD_MAP spec, used in the READMEs ("" for no spec).

    `name` turns a source column name into the name to show (e.g. its published `src_*` name). Code
    translations with more than MAX_INLINE_CODES entries are summarised as "translated (codes below)".
    """
    def _code(col):
        return f"`{name(col)}`"

    if spec is None:
        return ""
    if isinstance(spec, str):
        return _code(spec)
    kind, *args = spec
    if kind == "const":
        return f"always `{args[0]}`"
    if kind == "map":
        col, mapping = args
        if len(mapping) > MAX_INLINE_CODES:
            return f"{_code(col)}, translated (codes below)"
        pairs = ", ".join(f"{k} → {v or 'null'}" for k, v in mapping.items())
        return f"{_code(col)} ({pairs})"
    if kind == "prefix":
        return f"`{args[0]}` + {_code(args[1])}"
    if kind == "replace":
        return f"{_code(args[0])} with `{args[1]}` → `{args[2]}`"
    if kind == "join":
        return f" + `{args[0]}` + ".join(_code(c) for c in args[1])
    if kind == "first":
        return ", else ".join(describe_spec(s, name) for s in args[0])
    if kind in ("int", "date"):
        return _code(args[0])
    if kind == "area":
        return _code(args[0]) + (f" in {_code(args[1])} units" if args[1] else "") + ", as m²"
    if kind == "match":
        return f"{_code(args[0])} matches `{args[1]}`"
    if kind == "present":
        return f"{_code(args[0])} is present"
    raise ValueError(f"unknown field spec {spec!r}")
