import numpy as np
import pandas as pd


def read_parcel_keys(path, key_columns):
    """Candidate key columns of a parcels CSV, indexed by source_oid (blank -> NaN)."""
    kd = pd.read_csv(path, usecols=["source_oid"] + list(key_columns), dtype=str, keep_default_na=False)
    kd = kd.drop_duplicates("source_oid").set_index("source_oid")
    return kd.replace("", np.nan)
