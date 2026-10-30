import pandas as pd

from cadastre_gnaf.report.describe_column import describe_column
from cadastre_gnaf.report.descriptions import LINK_COLUMNS, SUMMARY_COLUMNS
from cadastre_gnaf.report.infer_type import infer_type
from cadastre_gnaf.report.source_fields import source_fields

SAMPLE_ROWS = 1000
EXAMPLE_CHARS = 60


def _example(values):
    v = next((x for x in values if x != ""), "")
    return v if len(v) <= EXAMPLE_CHARS else v[:EXAMPLE_CHARS - 3] + "..."


def dictionary_rows(config, files, sources, session=None):
    """One row per (file, column): type, description and an example value read from the file."""
    rows = []
    for f in files:
        sample = pd.read_csv(config.out_dir / f["file"], nrows=SAMPLE_ROWS, dtype=str, keep_default_na=False)
        if f["kind"] == "parcels":
            fields = source_fields(config, session, f["state"], sources[f["state"]])
            described = {c: describe_column(c, f["state"], fields) for c in sample.columns}
        else:
            known = LINK_COLUMNS if f["kind"] == "links" else SUMMARY_COLUMNS
            described = {c: known.get(c, (None, "")) for c in sample.columns}
        for c, (kind, text) in described.items():
            rows.append({"file": f["file"], "column": c, "type": kind or infer_type(sample[c]),
                         "description": text, "example": _example(sample[c])})
    return rows
