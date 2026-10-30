import pandas as pd


def count_rows(path, chunk=1_000_000):
    """Data rows in a CSV (or .csv.gz). Parses quotes, so values with embedded newlines count once."""
    return sum(len(c) for c in pd.read_csv(path, usecols=[0], dtype=str, chunksize=chunk))
