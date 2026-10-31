import pandas as pd

from cadastre_gnaf.constants import HARMONISED_COLUMNS, LEADING_COLUMNS, WORKING_COLUMNS
from cadastre_gnaf.publish.field_map import DROPPED_SOURCE_COLUMNS
from cadastre_gnaf.publish.harmonised_columns import harmonised_columns
from cadastre_gnaf.tabular.source_column_name import source_column_name


def published_frame(frame, state):
    """A chunk of a staged CSV (text) -> the published layout, the same for every state:

    LEADING_COLUMNS, HARMONISED_COLUMNS, the state's own attributes as `src_*` (candidate keys, ObjectID
    copies and service-computed shape areas dropped), then `wkt`.
    """
    skip = {*LEADING_COLUMNS, *WORKING_COLUMNS, "wkt"}
    source = [c for c in frame.columns
              if c not in skip and not c.startswith("key_") and c.lower() not in DROPPED_SOURCE_COLUMNS]
    out = pd.concat([frame[[c for c in LEADING_COLUMNS if c in frame]], harmonised_columns(frame, state),
                     frame[source].rename(columns=source_column_name)], axis=1)
    if "wkt" in frame:
        out["wkt"] = frame["wkt"]
    return out.reindex(columns=[*LEADING_COLUMNS, *HARMONISED_COLUMNS,
                                *[source_column_name(c) for c in source], *(["wkt"] if "wkt" in frame else [])])
