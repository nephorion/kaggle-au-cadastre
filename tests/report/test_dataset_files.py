from dataclasses import replace

from cadastre_gnaf.report import dataset_files


def test_lists_existing_files_with_rows_and_sizes(dataset_out):
    files = dataset_files(replace(dataset_out, states=("ACT", "NSW")))
    assert [(f["file"], f["kind"], f["state"], f["rows"]) for f in files] == [
        ("ACT_parcels.csv", "parcels", "ACT", 2),
        ("ACT_gnaf_address_parcel_links.csv", "links", "ACT", 1),
        ("summary.csv", "summary", None, 1)]
    assert files[0]["size_mb"] >= 0 and files[0]["description"].startswith("ACT land parcels")


def test_empty_folder(config):
    config.out_dir.mkdir()
    assert dataset_files(config) == []


def test_includes_parcels_with_addresses(dataset_out):
    (dataset_out.out_dir / "ACT_parcels_with_addresses.csv").write_text("source_oid,address_full\n1,x\n")
    kinds = [(f["file"], f["kind"]) for f in dataset_files(dataset_out)]
    assert ("ACT_parcels_with_addresses.csv", "parcel_addresses") in kinds
