import json

from cadastre_gnaf.storage import read_progress, write_progress


def test_creates_folder_and_writes_json(config):
    write_progress(config, "ACT", {"done": True})
    assert json.loads((config.progress_dir / "ACT.json").read_text()) == {"done": True}


def test_overwrites_and_round_trips(config):
    write_progress(config, "ACT", {"next": 1})
    write_progress(config, "ACT", {"next": 2})
    assert read_progress(config, "ACT") == {"next": 2}
