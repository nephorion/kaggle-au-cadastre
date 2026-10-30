from dataclasses import replace

from cadastre_gnaf.storage import links_path


def test_csv_path(config):
    assert links_path(config, "QLD") == config.out_dir / "QLD_gnaf_address_parcel_links.csv"


def test_compressed_path(config):
    assert links_path(replace(config, compress=True), "QLD").name.endswith(".csv.gz")
