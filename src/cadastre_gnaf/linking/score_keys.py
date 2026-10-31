def score_keys(parcel_keys, gnaf_keys):
    """[(key_column, matched, non_empty)] for each candidate, best match first."""
    stats = []
    for k in parcel_keys.columns:
        v = parcel_keys[k].dropna()
        stats.append((k, int(v.isin(gnaf_keys).sum()), len(v)))
    stats.sort(key=lambda s: -s[1])
    return stats
