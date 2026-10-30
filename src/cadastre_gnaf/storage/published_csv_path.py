CSV_DIR = "csv"


def published_csv_path(config, state):
    """Published parcels CSV of a state: <out>/csv/<STATE>_parcels.csv (gzipped with --compress)."""
    return config.out_dir / CSV_DIR / f"{state}_parcels{config.csv_ext}"
