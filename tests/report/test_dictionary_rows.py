from cadastre_gnaf.report import dataset_files, dictionary_rows
from cadastre_gnaf.sources import SOURCES


def rows_by_column(config):
    rows = dictionary_rows(config, dataset_files(config), SOURCES)
    return {(r["file"], r["column"]): r for r in rows}


def test_one_row_per_file_and_column(dataset_out):
    rows = rows_by_column(dataset_out)
    assert len([k for k in rows if k[0] == "ACT_parcels.csv"]) == 14
    assert len([k for k in rows if k[0] == "ACT_gnaf_address_parcel_links.csv"]) == 4
    assert len([k for k in rows if k[0] == "summary.csv"]) == 9


def test_types_descriptions_and_examples(dataset_out):
    rows = rows_by_column(dataset_out)
    addr = rows[("ACT_parcels.csv", "ADDRESSES")]
    assert addr["type"] == "string" and addr["description"] == "ACT source attribute `ADDRESSES`: Street addresses."
    assert addr["example"] == "1 A ST\n2 A ST"
    assert rows[("ACT_parcels.csv", "LAST_UPDATE")]["type"] == "date"
    assert rows[("ACT_parcels.csv", "EXTRA")]["type"] == "integer"             # not in the layer: inferred
    assert rows[("ACT_parcels.csv", "key_dist_blk")]["example"] == ""
    wkt = rows[("ACT_parcels.csv", "wkt")]["example"]
    assert wkt.endswith("...") and len(wkt) == 60
    assert rows[("ACT_gnaf_address_parcel_links.csv", "method")]["example"] == "legal_parcel_id"
    assert rows[("summary.csv", "licence")]["type"] == "string"


def test_parcels_with_addresses_columns(dataset_out):
    (dataset_out.out_dir / "ACT_parcels_with_addresses.csv").write_text(
        "source_oid,ADDRESSES,address_full,address_lon\n1,a,1 A ST,149.5\n")
    rows = rows_by_column(dataset_out)
    assert rows[("ACT_parcels_with_addresses.csv", "address_full")]["description"].startswith("One-line address")
    assert rows[("ACT_parcels_with_addresses.csv", "address_lon")]["type"] == "number"
    assert rows[("ACT_parcels_with_addresses.csv", "ADDRESSES")]["description"].startswith("ACT source attribute")
