from cadastre_gnaf.gnaf.read_table import read_table
from cadastre_gnaf.keys import norm_key


def read_address_parcels(source, state):
    """Live addresses with their LEGAL_PARCEL_ID and a normalised `key` column."""
    df = read_table(source, state, "ADDRESS_DETAIL", {"ADDRESS_DETAIL_PID", "LEGAL_PARCEL_ID", "DATE_RETIRED"})
    df["key"] = df["LEGAL_PARCEL_ID"].map(norm_key)
    return df
