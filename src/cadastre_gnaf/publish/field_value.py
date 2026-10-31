import re

import pandas as pd

UNITS_M2 = {"": 1.0, "m": 1.0, "meters": 1.0, "metres": 1.0, "m2": 1.0, "sqm": 1.0, "square meter": 1.0,
            "square meters": 1.0, "square metre": 1.0, "square metres": 1.0,
            "ha": 10_000.0, "hectare": 10_000.0, "hectares": 10_000.0}
_NUMBER_AND_UNIT = re.compile(r"^\s*([\d.,]+)\s*(.*?)\s*$")


def _col(frame, name):
    return frame[name].fillna("").astype(str) if name in frame else pd.Series("", index=frame.index, dtype=object)


def _area(values, units):
    out = []
    for v, u in zip(values, units):
        m = _NUMBER_AND_UNIT.match(v)
        if not m:
            out.append("")
            continue
        unit = (u or m.group(2)).strip().lower()
        try:
            a = float(m.group(1).replace(",", "")) * UNITS_M2[unit]
        except (KeyError, ValueError):
            a = 0.0
        out.append(f"{a:.2f}" if a > 0 else "")
    return out


def field_value(frame, spec, column=""):
    """Evaluate a FIELD_MAP spec (see field_map) on a chunk of source rows -> Series of text ("" = null).

    `column` is the harmonised column being filled; it decides how unlisted codes in a "map" spec are treated.
    """
    if spec is None:
        return pd.Series("", index=frame.index, dtype=object)
    if isinstance(spec, str):
        return _col(frame, spec).str.strip()
    kind, *args = spec
    if kind == "const":
        return pd.Series(args[0], index=frame.index, dtype=object)
    if kind == "map":
        col, mapping = args
        v = _col(frame, col).str.strip()
        other = "other" if column == "tenure" else ""
        return v.map(lambda x: mapping.get(x, other) if x else "")
    if kind == "prefix":
        text, col = args
        v = _col(frame, col).str.strip()
        return v.where(v == "", text + v)
    if kind == "replace":
        col, old, new = args
        return _col(frame, col).str.strip().str.replace(old, new, regex=False)
    if kind == "join":
        sep, cols = args
        parts = [_col(frame, c).str.strip() for c in cols]
        complete = pd.concat([p != "" for p in parts], axis=1).all(axis=1)
        joined = parts[0]
        for p in parts[1:]:
            joined = joined + sep + p
        return joined.where(complete, "")
    if kind == "first":
        out = pd.Series("", index=frame.index, dtype=object)
        for s in args[0]:
            out = out.where(out != "", field_value(frame, s, column))
        return out
    if kind == "int":
        num = pd.to_numeric(_col(frame, args[0]), errors="coerce")
        return num.map(lambda x: "" if pd.isna(x) else str(int(x)))
    if kind == "date":
        v = _col(frame, args[0]).str.strip().str[:10]
        return v.where(v.str.match(r"^\d{4}-\d{2}-\d{2}$") & (v < "2999"), "")
    if kind == "area":
        col, unit_col = args
        units = _col(frame, unit_col) if unit_col else pd.Series("", index=frame.index)
        if unit_col:                                    # a unit column that is empty means "unknown"
            units = units.where(units.str.strip() != "", "?")
        return pd.Series(_area(_col(frame, col), units), index=frame.index, dtype=object)
    if kind == "match":
        col, regex = args
        v = _col(frame, col).str.strip()
        return v.str.contains(regex, regex=True).map({True: "True", False: "False"}).where(v != "", "")
    if kind == "present":
        return (_col(frame, args[0]).str.strip() != "").map({True: "True", False: "False"})
    raise ValueError(f"unknown field spec {spec!r}")
