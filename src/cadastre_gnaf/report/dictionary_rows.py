import datetime as dt

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.report.describe_column import describe_column
from cadastre_gnaf.report.descriptions import SUMMARY_COLUMNS
from cadastre_gnaf.report.source_fields import source_fields

SAMPLE_ROWS = 1000
EXAMPLE_CHARS = 60


def _kind(t):
    """Arrow type -> data dictionary type."""
    if pa.types.is_integer(t):
        return "integer"
    if pa.types.is_floating(t):
        return "number"
    if pa.types.is_boolean(t):
        return "boolean"
    if pa.types.is_date(t):
        return "date"
    if pa.types.is_list(t):
        return f"list<{_kind(t.value_type)}>"
    return "string"


def _text(v):
    if v is None or v == "":
        return ""
    if isinstance(v, list):
        return ", ".join(_text(x) for x in v)
    return v.isoformat() if isinstance(v, dt.date) else str(v)


def _example(values):
    v = next((t for t in map(_text, values) if t), "")
    return v if len(v) <= EXAMPLE_CHARS else v[:EXAMPLE_CHARS - 3] + "..."


def dictionary_rows(config, files, sources, session=None):
    """One row per (file, column): type, description and an example value read from the file.

    CSV copies of the Parquet files are not repeated (their columns are the same).
    """
    rows = []
    for f in files:
        path = config.out_dir / f["file"]
        if f["kind"] == "parcels_csv":
            continue
        if f["kind"] == "parcels":
            pf = pq.ParquetFile(path)
            batch = next(pf.iter_batches(batch_size=SAMPLE_ROWS), None)
            fields = source_fields(config, session, f["state"], sources[f["state"]])
            for field in pf.schema_arrow:
                values = batch.column(field.name).to_pylist() if batch is not None else []
                rows.append({"file": f["file"], "column": field.name, "type": _kind(field.type),
                             "description": describe_column(field.name, f["state"], fields)[1],
                             "example": _example(values)})
        else:
            sample = pd.read_csv(path, nrows=SAMPLE_ROWS, dtype=str, keep_default_na=False)
            for c in sample.columns:
                kind, text = SUMMARY_COLUMNS.get(c, ("string", ""))
                rows.append({"file": f["file"], "column": c, "type": kind, "description": text,
                             "example": _example(sample[c])})
    return rows
