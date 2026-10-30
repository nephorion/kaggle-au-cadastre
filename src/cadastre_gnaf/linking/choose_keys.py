import numpy as np
import pandas as pd


def choose_keys(parcel_keys, ranked, gnaf_keys):
    """Per parcel: the first ranked candidate found in G-NAF, else the best-ranked non-empty one.

    Returns (chosen key Series, matched bool Series), both indexed like `parcel_keys`.
    """
    chosen = pd.Series(np.nan, index=parcel_keys.index, dtype=object)
    matched = pd.Series(False, index=parcel_keys.index)
    for k in ranked:                                   # first candidate that matches
        hit = parcel_keys[k].isin(gnaf_keys) & ~matched
        chosen[hit], matched[hit] = parcel_keys.loc[hit, k], True
    for k in ranked:                                   # otherwise best-ranked non-empty value
        fill = chosen.isna() & parcel_keys[k].notna()
        chosen[fill] = parcel_keys.loc[fill, k]
    return chosen, matched
