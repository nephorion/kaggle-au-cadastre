from cadastre_gnaf.report.descriptions import ESRI_TYPES, KEY_COLUMNS, PARCEL_COLUMNS


def describe_column(column, state, fields):
    """(type, description) of a parcels-file column; type is None when it has to be inferred from the data."""
    if column in PARCEL_COLUMNS:
        return PARCEL_COLUMNS[column]
    if column.startswith("key_"):
        return "string", KEY_COLUMNS.get(column, "Candidate G-NAF `LEGAL_PARCEL_ID` key.")
    name = column[4:] if column.startswith("src_") and column[4:] in fields else column
    f = fields.get(name)
    if f is None:
        return None, f"{state} source attribute `{name}`."
    alias = (f.get("alias") or "").strip()
    text = f"{state} source attribute `{name}`" + (f": {alias}" if alias and alias.lower() != name.lower() else "")
    kind = ESRI_TYPES.get(f.get("type"))
    if kind == "date":
        text += " (ISO date, converted from Esri epoch milliseconds)"
    return kind, text + "."
