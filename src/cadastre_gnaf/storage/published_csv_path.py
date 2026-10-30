def published_csv_path(config, state):
    """Published parcels CSV of a state (gzipped with --compress)."""
    return config.out_dir / f"{state}_parcels{config.csv_ext}"
