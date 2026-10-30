def parcels_path(config, state):
    return config.out_dir / f"{state}_parcels{config.csv_ext}"
