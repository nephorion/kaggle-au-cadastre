import pandas as pd

from cadastre_gnaf.constants import GNAF_COLUMNS, LIST_SEPARATOR


def _joined(links, column):
    """source_oid -> sorted, distinct values of `column` joined with LIST_SEPARATOR."""
    d = links[["source_oid", column]].drop_duplicates().sort_values(["source_oid", column])
    return d.groupby("source_oid")[column].agg(LIST_SEPARATOR.join)


def rewrite_parcels(path, key_count, chosen, matched, links, compression=None, chunk=200_000):
    """Rewrite a parcels CSV with the G-NAF columns, de-duplicated by source_oid.

    `links` has one row per linked address: address_detail_pid, source_oid (str) and method.
    """
    pids, methods = _joined(links, "address_detail_pid"), _joined(links, "method")
    counts = links.groupby("source_oid")["address_detail_pid"].nunique()
    tmp = path.with_name(path.name + ".tmp")
    seen, first = set(), True
    pos = 2 + key_count                                 # after state, source_oid and the key columns
    for c in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunk):
        c = c.drop(columns=[x for x in GNAF_COLUMNS if x in c])
        c = c[~c["source_oid"].isin(seen)].drop_duplicates("source_oid")
        seen.update(c["source_oid"])
        oid = c["source_oid"]
        c.insert(pos, "gnaf_legal_parcel_id", oid.map(chosen).fillna(""))
        c.insert(pos + 1, "gnaf_key_matched", oid.map(matched).fillna(False))
        c.insert(pos + 2, "gnaf_address_count", oid.map(counts).fillna(0).astype(int))
        c.insert(pos + 3, "gnaf_address_detail_pids", oid.map(pids).astype(object).fillna(""))
        c.insert(pos + 4, "gnaf_link_methods", oid.map(methods).astype(object).fillna(""))
        c.to_csv(tmp, mode="w" if first else "a", header=first, index=False, compression=compression)
        first = False
    tmp.replace(path)
