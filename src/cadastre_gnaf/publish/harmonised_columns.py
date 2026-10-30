import pandas as pd

from cadastre_gnaf.constants import HARMONISED_COLUMNS
from cadastre_gnaf.publish.field_map import FIELD_MAP
from cadastre_gnaf.publish.field_value import field_value
from cadastre_gnaf.publish.geometry_measures import geometry_measures


def harmonised_columns(frame, state):
    """The harmonised columns (HARMONISED_COLUMNS, as text, "" = null) for a chunk of a state's staged rows."""
    fields = FIELD_MAP.get(state, {})
    out = pd.DataFrame({c: field_value(frame, fields.get(c), c) for c in HARMONISED_COLUMNS}, index=frame.index)
    measures = geometry_measures(frame["wkt"] if "wkt" in frame else pd.Series("", index=frame.index))
    for c in measures:
        out[c] = measures[c]
    gnaf = frame["gnaf_locality"].fillna("") if "gnaf_locality" in frame else ""
    out["locality"] = pd.Series(gnaf, index=frame.index).where(lambda s: s != "", out["locality"]).str.upper()
    return out[list(HARMONISED_COLUMNS)]
