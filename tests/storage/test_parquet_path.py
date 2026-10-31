from cadastre_gnaf.storage import parquet_path


def test_parquet_in_out_dir(config):
    assert parquet_path(config, "NSW") == config.out_dir / "parquet" / "NSW_parcels.parquet"
