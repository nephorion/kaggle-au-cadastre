from cadastre_gnaf.constants import BASE_COLUMNS


def output_columns(key_columns, attr_names, include_wkt=True):
    """Column order of a parcels CSV (before G-NAF finalisation)."""
    cols = ["state", "source_oid"] + list(key_columns) + ["point_lon", "point_lat"]
    cols += [c if c not in BASE_COLUMNS else f"src_{c}" for c in attr_names]
    return cols + (["wkt"] if include_wkt else [])
