import datetime as dt


def _cell(v):
    return str(v).replace("|", r"\|").replace("\n", " ")


def dictionary_markdown(rows, files, built=None):
    """data_dictionary.md: one table of columns per file."""
    built = built or dt.datetime.now()
    about = {f["file"]: f for f in files}
    out = ["# Data dictionary", "",
           "Every column of every file in this dataset. The same content is in `data_dictionary.csv`.",
           "Each `<STATE>_parcels.csv` has the same columns as its `.parquet` file; list columns are written "
           "as `|`-separated text.",
           "Coordinates are EPSG:4326 (WGS 84 / GDA2020 lon/lat). Empty cells mean the value is missing.", ""]
    for name in dict.fromkeys(r["file"] for r in rows):
        f = about.get(name, {})
        out += [f"## `{name}`", ""]
        if f:
            out += [f"{f['description']}. {f['rows']:,} rows.", ""]
        out += ["| Column | Type | Description | Example |", "|---|---|---|---|"]
        out += [f"| `{r['column']}` | {r['type']} | {_cell(r['description'])} | "
                + (f"`{_cell(r['example'])}`" if r["example"] else "") + " |"
                for r in rows if r["file"] == name]
        out.append("")
    out.append(f"Generated {built.isoformat(timespec='minutes')}.")
    return "\n".join(out) + "\n"
