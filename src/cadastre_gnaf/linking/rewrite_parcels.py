import pandas as pd

from cadastre_gnaf.constants import GEOMETRY_GROUP_COLUMNS, GNAF_COLUMNS, LEADING_COLUMNS, LIST_SEPARATOR


def _joined(links, column):
    """source_oid -> sorted, distinct values of `column` joined with LIST_SEPARATOR."""
    d = links[["source_oid", column]].drop_duplicates().sort_values(["source_oid", column])
    return d.groupby("source_oid")[column].agg(LIST_SEPARATOR.join)


def rewrite_parcels(path, chosen, matched, links, groups=None, compression=None, chunk=200_000):
    """Rewrite a parcels CSV with the G-NAF and geometry-group columns, de-duplicated by source_oid.

    `links` has one row per linked address: address_detail_pid, source_oid (str) and method.
    `groups` comes from geometry_groups (None: every parcel is its own group). Columns are put in the
    order shared by all states: LEADING_COLUMNS, then the state's own columns, then `wkt`.
    """
    pids, methods = _joined(links, "address_detail_pid"), _joined(links, "method")
    counts = links.groupby("source_oid")["address_detail_pid"].nunique()
    tmp = path.with_name(path.name + ".tmp")
    seen, first = set(), True
    for c in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunk):
        c = c.drop(columns=[x for x in (*GNAF_COLUMNS, *GEOMETRY_GROUP_COLUMNS) if x in c])
        c = c[~c["source_oid"].isin(seen)].drop_duplicates("source_oid")
        seen.update(c["source_oid"])
        oid = c["source_oid"]
        c["gnaf_legal_parcel_id"] = oid.map(chosen).astype(object).fillna("")
        c["gnaf_key_matched"] = oid.map(matched).astype(object).fillna(False)
        c["gnaf_address_count"] = oid.map(counts).fillna(0).astype(int)
        c["gnaf_address_detail_pids"] = oid.map(pids).astype(object).fillna("")
        c["gnaf_link_methods"] = oid.map(methods).astype(object).fillna("")
        if groups is None:
            c["geometry_group_id"], c["geometry_group_size"] = oid, 1
        else:
            c["geometry_group_id"] = oid.map(groups["geometry_group_id"]).fillna(oid)
            c["geometry_group_size"] = oid.map(groups["geometry_group_size"]).fillna(1).astype(int)
        rest = [x for x in c.columns if x not in LEADING_COLUMNS and x != "wkt"]
        c = c[[*LEADING_COLUMNS, *rest, *(["wkt"] if "wkt" in c else [])]]
        c.to_csv(tmp, mode="w" if first else "a", header=first, index=False, compression=compression)
        first = False
    tmp.replace(path)
