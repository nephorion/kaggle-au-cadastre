from cadastre_gnaf.report.descriptions import ESRI_TYPES, HARMONISED_COLUMNS, KEY_COLUMNS, PARCEL_COLUMNS
from cadastre_gnaf.tabular.source_column_name import source_column_name


def describe_column(column, state, fields):
    """(type, description) of a parcels-file column; type is None when the source does not say.

    Source attributes may be named as published by the state or as `src_<snake_case>`.
    """
    if column in PARCEL_COLUMNS:
        return PARCEL_COLUMNS[column]
    if column in HARMONISED_COLUMNS:
        return HARMONISED_COLUMNS[column]
    if column.startswith("key_"):
        return "string", KEY_COLUMNS.get(column, "Candidate G-NAF `LEGAL_PARCEL_ID` key.")
    f = fields.get(column) or {source_column_name(n): v for n, v in fields.items()}.get(column)
    name = f["name"] if f else (column[4:] if column.startswith("src_") else column)
    if f is None:
        return None, f"{state} source attribute `{name}`."
    alias = (f.get("alias") or "").strip()
    text = f"{state} source attribute `{name}`" + (f": {alias}" if alias and alias.lower() != name.lower() else "")
    kind = ESRI_TYPES.get(f.get("type"))
    if kind == "date":
        text += " (ISO date, converted from Esri epoch milliseconds)"
    return kind, text + "."
