import numpy as np
import pandas as pd

from cadastre_gnaf.keys import key_names
from cadastre_gnaf.storage import append_csv, parcels_path, write_progress
from cadastre_gnaf.tabular import output_columns, rows_from_items

CHUNK_ROWS = 100_000


def load_local_state(config, state, source, path):
    """Licensed/purchased data (SA, NT, or a WA subscription extract) read with geopandas."""
    import geopandas as gpd

    gdf = gpd.read_file(path)
    gdf = gdf.set_crs(4326) if gdf.crs is None else gdf.to_crs(4326)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
    attr_names = [c for c in gdf.columns if c != gdf.geometry.name]
    gdf["__oid"] = np.arange(1, len(gdf) + 1)
    cols = output_columns(key_names(source.keys), attr_names, config.include_wkt)
    out, first = parcels_path(config, state), True
    for start in range(0, len(gdf), CHUNK_ROWS):
        part = gdf.iloc[start:start + CHUNK_ROWS]
        pts = part.geometry.representative_point()
        wkts = (part.geometry.to_wkt(rounding_precision=config.decimals) if config.include_wkt
                else [""] * len(part))
        recs = part[attr_names + ["__oid"]].to_dict("records")
        items = []
        for rec, w, p in zip(recs, wkts, pts):
            rec = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in rec.items()}
            items.append((rec, w, round(p.x, config.decimals + 1), round(p.y, config.decimals + 1)))
        rows = rows_from_items(state, source.keys, items, set(), "__oid", config.include_wkt)
        append_csv(out, pd.DataFrame(rows), cols, first, config.compression)
        first = False
    write_progress(config, state, {"rows": len(gdf), "expected": len(gdf), "done": True,
                                   "columns": cols, "source": str(path)})
    print(f"[{state}] {len(gdf):,} rows from {path} -> {out}")
