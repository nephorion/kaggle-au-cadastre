import pandas as pd

from cadastre_gnaf.gnaf.read_table import read_table


def read_address_points(source, state):
    """Live default geocodes (numeric LONGITUDE/LATITUDE; rows without coordinates dropped)."""
    df = read_table(source, state, "ADDRESS_DEFAULT_GEOCODE",
                    {"ADDRESS_DETAIL_PID", "LONGITUDE", "LATITUDE", "DATE_RETIRED"})
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    return df.dropna(subset=["LONGITUDE", "LATITUDE"])
