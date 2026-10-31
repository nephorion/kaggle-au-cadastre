import pandas as pd

from cadastre_gnaf.report import write_summary
from cadastre_gnaf.sources import Source

SOURCES = {"ACT": Source(url="http://act", keys=dict, licence="(c) ACT")}


def test_writes_summary_csv_and_attribution(config, capsys):
    summary = write_summary(config, [{"state": "ACT", "parcels": 3}], SOURCES)
    assert summary["parcels_written"].tolist() == [3]
    assert pd.read_csv(config.out_dir / "summary.csv")["state"].tolist() == ["ACT"]
    assert "**ACT**: (c) ACT" in (config.out_dir / "ATTRIBUTION.md").read_text(encoding="utf-8")
    out = capsys.readouterr().out
    assert "summary.csv" in out and "ATTRIBUTION.md" in out
