from dataclasses import replace

from cadastre_gnaf.report import dataset_files


def test_lists_published_files_with_rows_and_sizes(dataset_out):
    (dataset_out.out_dir / "ACT_gnaf_address_parcel_links.csv").write_text("x\n1\n")     # not part of the dataset
    files = dataset_files(replace(dataset_out, states=("ACT", "NSW")))
    assert [(f["file"], f["kind"], f["state"], f["rows"]) for f in files] == [
        ("ACT_parcels.parquet", "parcels", "ACT", 2),
        ("summary.csv", "summary", None, 1)]
    assert files[0]["size_mb"] >= 0 and files[0]["description"].startswith("ACT land parcels")


def test_csv_twin_listed_after_parquet(dataset_out):
    (dataset_out.out_dir / "ACT_parcels.csv").write_text("state\nACT\nACT\n")
    files = dataset_files(dataset_out)
    assert [(f["file"], f["kind"], f.get("same_as")) for f in files[:2]] == [
        ("ACT_parcels.parquet", "parcels", None), ("ACT_parcels.csv", "parcels_csv", "ACT_parcels.parquet")]
    assert files[1]["rows"] == 2 and "`|`-separated" in files[1]["description"]


def test_empty_folder(config):
    config.out_dir.mkdir()
    assert dataset_files(config) == []


def test_covers_states_outside_this_run(dataset_out):
    assert dataset_files(replace(dataset_out, states=("VIC",)))[0]["file"] == "ACT_parcels.parquet"
