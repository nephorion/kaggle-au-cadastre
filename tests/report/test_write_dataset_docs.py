import json

import pandas as pd

from cadastre_gnaf.report import write_dataset_docs
from cadastre_gnaf.sources import SOURCES


def test_writes_all_docs(dataset_out, capsys):
    rows = write_dataset_docs(dataset_out, None, SOURCES)
    out = dataset_out.out_dir
    dd = pd.read_csv(out / "data_dictionary.csv", keep_default_na=False)
    assert list(dd.columns) == ["file", "column", "type", "description", "example"] and len(dd) == len(rows)
    assert "## `parquet/ACT_parcels.parquet`" in (out / "data_dictionary.md").read_text(encoding="utf-8")
    readme = (out / "README.md").read_text(encoding="utf-8")
    assert "| ACT | 2 | 50.0% | 4 | 50.0% |" in readme and "- **ACT**: (c) ACT" in readme
    meta = json.loads((out / "dataset-metadata.json").read_text(encoding="utf-8"))
    assert meta["id"] == dataset_out.kaggle_id and meta["description"] == readme
    assert [r["path"] for r in meta["resources"]] == ["parquet/ACT_parcels.parquet", "summary.csv"]
    pids = next(f for f in meta["resources"][0]["schema"]["fields"] if f["name"] == "gnaf_address_detail_pids")
    assert pids["type"] == "string"
    assert "dataset-metadata.json" in capsys.readouterr().out


def test_works_without_summary_or_attribution(dataset_out):
    (dataset_out.out_dir / "summary.csv").unlink()
    (dataset_out.out_dir / "ATTRIBUTION.md").unlink()
    write_dataset_docs(dataset_out, None, SOURCES)
    assert "## Coverage" not in (dataset_out.out_dir / "README.md").read_text(encoding="utf-8")
