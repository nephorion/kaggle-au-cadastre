import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.report import dataset_files, dictionary_rows
from cadastre_gnaf.sources import SOURCES
from cadastre_gnaf.storage import parquet_path


def rows_by_column(config):
    rows = dictionary_rows(config, dataset_files(config), SOURCES)
    return {(r["file"], r["column"]): r for r in rows}


def test_one_row_per_file_and_column(dataset_out):
    rows = rows_by_column(dataset_out)
    assert len([k for k in rows if k[0] == "parquet/ACT_parcels.parquet"]) == 11
    assert len([k for k in rows if k[0] == "summary.csv"]) == 9


def test_types_come_from_the_parquet_schema(dataset_out):
    rows = rows_by_column(dataset_out)
    kinds = {c: rows[("parquet/ACT_parcels.parquet", c)]["type"] for c in
             ("source_oid", "gnaf_key_matched", "point_lon", "LAST_UPDATE", "gnaf_address_detail_pids", "wkt")}
    assert kinds == {"source_oid": "integer", "gnaf_key_matched": "boolean", "point_lon": "number",
                     "LAST_UPDATE": "date", "gnaf_address_detail_pids": "list<string>", "wkt": "string"}
    assert rows[("summary.csv", "address_link_rate")]["type"] == "number"


def test_descriptions_and_examples(dataset_out):
    rows = rows_by_column(dataset_out)
    addr = rows[("parquet/ACT_parcels.parquet", "ADDRESSES")]
    assert addr["description"] == "ACT source attribute `ADDRESSES`: Street addresses."
    assert addr["example"] == "1 A ST\n2 A ST"
    assert rows[("parquet/ACT_parcels.parquet", "gnaf_address_detail_pids")]["example"] == "GAACT1, GAACT2"
    assert rows[("parquet/ACT_parcels.parquet", "LAST_UPDATE")]["example"] == "2026-01-02"
    assert rows[("parquet/ACT_parcels.parquet", "gnaf_key_matched")]["example"] == "True"
    assert rows[("parquet/ACT_parcels.parquet", "key_dist_blk")]["example"] == ""
    wkt = rows[("parquet/ACT_parcels.parquet", "wkt")]["example"]
    assert wkt.endswith("...") and len(wkt) == 60
    assert rows[("summary.csv", "licence")]["example"] == "(c) ACT"


def test_csv_twin_not_repeated(dataset_out):
    (dataset_out.out_dir / "csv").mkdir()
    (dataset_out.out_dir / "csv" / "ACT_parcels.csv").write_text("state\nACT\n")
    assert not [k for k in rows_by_column(dataset_out) if k[0] == "csv/ACT_parcels.csv"]


def test_empty_parquet_file(dataset_out):
    pq.write_table(pa.table({"source_oid": pa.array([], pa.int64())}), parquet_path(dataset_out, "ACT"))
    rows = rows_by_column(dataset_out)
    assert rows[("parquet/ACT_parcels.parquet", "source_oid")]["example"] == ""
