import numpy as np
import pandas as pd
import shapely
from pyproj import Transformer

_TO_ALBERS = Transformer.from_crs(4326, 3577, always_xy=True)      # GDA94 Australian Albers, equal-area


def _project(coords):
    x, y = _TO_ALBERS.transform(coords[:, 0], coords[:, 1])
    return np.column_stack([x, y])


def geometry_measures(wkt):
    """WKT polygons (EPSG:4326) -> area_m2, perimeter_m and is_multipart as text ("" where there is no polygon).

    Measured in Australian Albers (EPSG:3577), so areas are comparable across states. Invalid polygons are
    repaired first so self-intersections do not distort the area.
    """
    w = pd.Series(wkt, dtype=object).fillna("").astype(str)
    has = (w != "").to_numpy()
    out = pd.DataFrame({"area_m2": "", "perimeter_m": "", "is_multipart": ""}, index=w.index, dtype=object)
    if not has.any():
        return out
    geoms = shapely.from_wkt(w[has].to_numpy(), on_invalid="ignore")
    ok = ~shapely.is_missing(geoms)
    parts = shapely.get_num_geometries(geoms)                      # as published, before any repair
    bad = ok & ~shapely.is_valid(geoms)
    geoms[bad] = shapely.make_valid(geoms[bad])
    projected = shapely.transform(geoms, _project)
    area, length = shapely.area(projected), shapely.length(projected)
    out.loc[has, "area_m2"] = np.where(ok, np.char.mod("%.1f", np.nan_to_num(area)), "")
    out.loc[has, "perimeter_m"] = np.where(ok, np.char.mod("%.1f", np.nan_to_num(length)), "")
    out.loc[has, "is_multipart"] = np.where(ok, np.where(parts > 1, "True", "False"), "")
    return out
