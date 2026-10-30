import pandas as pd

from cadastre_gnaf.constants import ADDRESS_COLUMNS


def write_parcel_addresses(parcels_csv, links, addresses, out, compression=None, chunk=200_000):
    """Write every parcel left-joined to its linked addresses: one row per parcel and address.

    Parcels without an address get a single row with empty address columns. `links` is the
    address -> parcel link table and `addresses` comes from read_addresses. Returns the rows written.
    """
    lk = links[["source_oid", "address_detail_pid", "method"]].astype(str)
    lk = lk.drop_duplicates(["source_oid", "address_detail_pid"]).rename(columns={"method": "address_link_method"})
    lk = lk.merge(addresses, on="address_detail_pid", how="left")
    rows, first = 0, True
    for c in pd.read_csv(parcels_csv, dtype=str, keep_default_na=False, chunksize=chunk):
        cols = [x for x in c.columns if x != "wkt"] + ADDRESS_COLUMNS + (["wkt"] if "wkt" in c else [])
        m = c.merge(lk, on="source_oid", how="left").reindex(columns=cols)
        m.to_csv(out, mode="w" if first else "a", header=first, index=False, compression=compression)
        rows, first = rows + len(m), False
    return rows
