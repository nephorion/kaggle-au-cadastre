from dataclasses import replace

from cadastre_gnaf.storage import published_csv_path


def test_csv_in_out_dir(config):
    assert published_csv_path(config, "NSW") == config.out_dir / "NSW_parcels.csv"


def test_compressed(config):
    assert published_csv_path(replace(config, compress=True), "NSW").name == "NSW_parcels.csv.gz"
