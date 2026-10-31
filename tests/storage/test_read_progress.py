import json

from cadastre_gnaf.storage import read_progress


def test_missing_progress_is_empty(config):
    assert read_progress(config, "ACT") == {}


def test_reads_saved_progress(config):
    config.progress_dir.mkdir(parents=True)
    (config.progress_dir / "ACT.json").write_text(json.dumps({"next": 10, "rows": 5}))
    assert read_progress(config, "ACT") == {"next": 10, "rows": 5}
