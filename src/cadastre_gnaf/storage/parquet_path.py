PARQUET_DIR = "parquet"


def parquet_path(config, state):
    """Published parcels file of a state: <out>/parquet/<STATE>_parcels.parquet."""
    return config.out_dir / PARQUET_DIR / f"{state}_parcels.parquet"
