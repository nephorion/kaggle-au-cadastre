import datetime as dt

import pandas as pd
import pyarrow as pa

from cadastre_gnaf.constants import LIST_SEPARATOR
from cadastre_gnaf.publish.arrow_type import arrow_type


def _date(v):
    try:
        return dt.date.fromisoformat(v[:10])
    except (TypeError, ValueError):
        return None


def to_arrow(values, kind):
    """CSV text values (empty = missing) -> Arrow array of the given dictionary type.

    Values that do not parse as the type become null.
    """
    v = pd.Series(values, dtype=str)
    missing = v == ""
    if kind in ("integer", "number"):
        num = pd.to_numeric(v.where(~missing), errors="coerce")
        if kind == "integer":
            num = num.where(num == num.round()).astype("Int64")
        return pa.array(num, type=arrow_type(kind), from_pandas=True)
    if kind == "boolean":
        return pa.array(v.str.lower().map({"true": True, "false": False}), type=pa.bool_(), from_pandas=True)
    if kind == "date":
        return pa.array([None if m else _date(x) for x, m in zip(v, missing)], type=pa.date32())
    if kind == "list<string>":
        return pa.array([None if m else x.split(LIST_SEPARATOR) for x, m in zip(v, missing)],
                        type=pa.list_(pa.string()))
    return pa.array(v.where(~missing), type=pa.string(), from_pandas=True)
