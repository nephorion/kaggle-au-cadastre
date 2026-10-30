def parquet_path(config, state):
    """Published parcels file of a state."""
    return config.out_dir / f"{state}_parcels.parquet"
