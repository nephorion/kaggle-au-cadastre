import pandas as pd


def key_links(address_parcels, chosen, matched):
    """Address -> parcel links for parcels whose chosen key equals a G-NAF LEGAL_PARCEL_ID."""
    pk = pd.DataFrame({"source_oid": chosen[matched].index, "key": chosen[matched].values})
    links = address_parcels.merge(pk, on="key", how="inner")[["ADDRESS_DETAIL_PID", "LEGAL_PARCEL_ID", "source_oid"]]
    links.columns = ["address_detail_pid", "legal_parcel_id", "source_oid"]
    links["method"] = "legal_parcel_id"
    return links
