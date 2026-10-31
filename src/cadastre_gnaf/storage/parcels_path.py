def parcels_path(config, state):
    """Staged (working) parcels CSV of a state."""
    return config.staging_dir / f"{state}_parcels{config.csv_ext}"
