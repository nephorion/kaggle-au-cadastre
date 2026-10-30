import pandas as pd

from cadastre_gnaf.constants import GNAF_COLUMNS


def rewrite_parcels(path, key_count, chosen, matched, counts, compression=None, chunk=200_000):
    """Rewrite a parcels CSV with the three G-NAF columns, de-duplicated by source_oid."""
    tmp = path.with_name(path.name + ".tmp")
    seen, first = set(), True
    pos = 2 + key_count                                 # after state, source_oid and the key columns
    for c in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunk):
        c = c.drop(columns=[x for x in GNAF_COLUMNS if x in c])
        c = c[~c["source_oid"].isin(seen)].drop_duplicates("source_oid")
        seen.update(c["source_oid"])
        c.insert(pos, "gnaf_legal_parcel_id", c["source_oid"].map(chosen).fillna(""))
        c.insert(pos + 1, "gnaf_key_matched", c["source_oid"].map(matched).fillna(False))
        c.insert(pos + 2, "gnaf_address_count", c["source_oid"].map(counts).fillna(0).astype(int))
        c.to_csv(tmp, mode="w" if first else "a", header=first, index=False, compression=compression)
        first = False
    tmp.replace(path)
