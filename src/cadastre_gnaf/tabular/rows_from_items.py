from cadastre_gnaf.constants import BASE_COLUMNS
from cadastre_gnaf.tabular.epoch_ms_to_date import epoch_ms_to_date


def rows_from_items(state, key_builder, items, date_fields, oid_field, include_wkt=True):
    """items: iterable of (attrs, wkt, lon, lat) -> list of row dicts."""
    rows = []
    for attrs, wkt, lon, lat in items:
        row = {"state": state, "source_oid": attrs.get(oid_field)}
        row.update(key_builder(attrs))
        row["point_lon"], row["point_lat"] = lon, lat
        for k, v in attrs.items():
            if k in date_fields:
                v = epoch_ms_to_date(v)
            row[k if k not in BASE_COLUMNS else f"src_{k}"] = v
        if include_wkt:
            row["wkt"] = wkt
        rows.append(row)
    return rows
