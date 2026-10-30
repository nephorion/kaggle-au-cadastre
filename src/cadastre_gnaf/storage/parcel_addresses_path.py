def parcel_addresses_path(config, state):
    return config.out_dir / f"{state}_parcels_with_addresses{config.csv_ext}"
