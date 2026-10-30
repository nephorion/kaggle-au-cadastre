import pandas as pd

from cadastre_gnaf.gnaf.open_table import open_table


def read_table(source, state, table, usecols):
    """Read selected columns of a G-NAF PSV table as strings, dropping retired rows."""
    with open_table(source, state, table) as fh:
        df = pd.read_csv(fh, sep="|", dtype=str, usecols=lambda c: c in usecols, keep_default_na=False)
    if "DATE_RETIRED" in df:
        df = df[df["DATE_RETIRED"] == ""].drop(columns="DATE_RETIRED")
    return df
