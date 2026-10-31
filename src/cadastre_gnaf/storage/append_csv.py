from pathlib import Path


def append_csv(path, df, columns, first, compression=None):
    """Write (first=True) or append a chunk to a CSV, in a fixed column order."""
    if first:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.reindex(columns=columns).to_csv(path, mode="w" if first else "a", header=first, index=False,
                                       compression=compression)
