import hashlib

import pandas as pd


def geometry_groups(path, chunk=500_000):
    """Parcels with an identical WKT polygon (e.g. stacked strata lots) form a group.

    Returns a DataFrame indexed by source_oid with `geometry_group_id` (the lowest source_oid in the
    group) and `geometry_group_size`. Parcels without WKT are each their own group; None if the file
    has no `wkt` column.
    """
    if "wkt" not in pd.read_csv(path, nrows=0).columns:
        return None
    parts = []
    for c in pd.read_csv(path, usecols=["source_oid", "wkt"], dtype=str, keep_default_na=False, chunksize=chunk):
        geom = [hashlib.md5(w.encode()).hexdigest() if w else f"oid:{o}" for o, w in zip(c["source_oid"], c["wkt"])]
        parts.append(pd.DataFrame({"source_oid": c["source_oid"].to_numpy(), "geom": geom}))
    d = pd.concat(parts, ignore_index=True).drop_duplicates("source_oid")
    d["order"] = pd.to_numeric(d["source_oid"], errors="coerce")
    d = d.sort_values(["order", "source_oid"], na_position="last")
    g = d.groupby("geom", sort=False)["source_oid"]
    return pd.DataFrame({"geometry_group_id": g.transform("first").to_numpy(),
                         "geometry_group_size": g.transform("size").to_numpy()},
                        index=pd.Index(d["source_oid"].to_numpy(), name="source_oid"))
