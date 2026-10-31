from dataclasses import replace

from cadastre_gnaf.storage import parcels_path


def test_csv_path(config):
    assert parcels_path(config, "NSW") == config.work_dir / "staging" / "NSW_parcels.csv"


def test_compressed_path(config):
    assert parcels_path(replace(config, compress=True), "NSW").name == "NSW_parcels.csv.gz"
