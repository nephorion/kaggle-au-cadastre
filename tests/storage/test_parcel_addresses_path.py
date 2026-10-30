from dataclasses import replace

from cadastre_gnaf.storage import parcel_addresses_path


def test_csv_path(config):
    assert parcel_addresses_path(config, "NSW") == config.out_dir / "NSW_parcels_with_addresses.csv"


def test_compressed_path(config):
    assert parcel_addresses_path(replace(config, compress=True), "NSW").name == "NSW_parcels_with_addresses.csv.gz"
