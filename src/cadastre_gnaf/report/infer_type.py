import pandas as pd


def infer_type(values):
    """Best-guess column type ("integer", "number", "date" or "string") from sample string values."""
    v = pd.Series(values, dtype=str)
    v = v[v != ""]
    if v.empty:
        return "string"
    num = pd.to_numeric(v, errors="coerce")
    if num.notna().all():
        return "integer" if (num == num.round()).all() and not v.str.contains(r"[.eE]").any() else "number"
    if v.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        return "date"
    return "string"
