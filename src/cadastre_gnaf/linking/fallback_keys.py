import numpy as np
import pandas as pd


def fallback_keys(parcel_keys):
    """Without G-NAF: first non-empty candidate per parcel, nothing marked as matched."""
    if len(parcel_keys.columns):
        chosen = parcel_keys.bfill(axis=1).iloc[:, 0]
    else:
        chosen = pd.Series(np.nan, index=parcel_keys.index, dtype=object)
    return chosen, pd.Series(False, index=parcel_keys.index)
