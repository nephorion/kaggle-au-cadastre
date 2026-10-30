import datetime as dt

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.constants import HARMONISED_COLUMNS, LEADING_COLUMNS
from cadastre_gnaf.publish import publish_state
from cadastre_gnaf.sources import Source
from cadastre_gnaf.storage import parcels_path, parquet_path, published_csv_path, write_progress

SOURCE = Source(url="http://x", keys=dict, licence="l")
SQUARE = "POLYGON ((149 -35,149 -34.999,149.001 -34.999,149.001 -35,149 -35))"
CSV = ("state,source_oid,gnaf_legal_parcel_id,gnaf_key_matched,gnaf_address_count,gnaf_address_detail_pids,"
       "gnaf_link_methods,geometry_group_id,geometry_group_size,point_lon,point_lat,key_dist_blk,OBJECTID,"
       "BLOCK_NUMBER,LAST_UPDATE,Shape__Area,gnaf_locality,wkt\n"
       f'ACT,1,CANB/1,True,2,GA1|GA2,legal_parcel_id,1,1,149.5,-35.5,CANB/1,1,0041,2026-01-02,99,BRADDON,"{SQUARE}"\n'
       "ACT,2,,False,0,,,2,1,150.5,-35.5,,2,,,,,\n")


def stage(config):
    staged = parcels_path(config, "ACT")
    staged.parent.mkdir(parents=True)
    staged.write_text(CSV)
    write_progress(config, "ACT", {"fields": [{"name": "BLOCK_NUMBER", "type": "esriFieldTypeString"},
                                              {"name": "LAST_UPDATE", "type": "esriFieldTypeDate"}]})


def test_shared_layout_and_types(config):
    stage(config)
    assert publish_state(config, None, "ACT", SOURCE) == 2
    t = pq.read_table(parquet_path(config, "ACT"))
    assert t.column_names == [*LEADING_COLUMNS, *HARMONISED_COLUMNS, "src_block_number", "src_last_update", "wkt"]
    types = {f.name: f.type for f in t.schema}
    assert types["source_oid"] == pa.int64() and types["gnaf_key_matched"] == pa.bool_()
    assert types["gnaf_address_detail_pids"] == pa.list_(pa.string())
    assert types["area_m2"] == pa.float64() and types["is_multipart"] == pa.bool_()
    assert types["source_last_updated"] == pa.date32() and types["src_last_update"] == pa.date32()
    row = t.to_pylist()[0]
    assert row["src_block_number"] == "0041"                    # string field keeps leading zeros
    assert row["lot"] == "0041" and row["tenure"] == "lease" and row["locality"] == "BRADDON"
    assert row["source_last_updated"] == dt.date(2026, 1, 2)
    assert 9_800 < row["area_m2"] < 10_400                      # ~91 m x 111 m
    assert row["gnaf_address_detail_pids"] == ["GA1", "GA2"]
    assert t.to_pylist()[1]["gnaf_address_detail_pids"] is None and t.to_pylist()[1]["area_m2"] is None


def test_csv_has_the_same_columns_and_rows(config):
    stage(config)
    publish_state(config, None, "ACT", SOURCE)
    csv = pd.read_csv(published_csv_path(config, "ACT"), dtype=str, keep_default_na=False)
    assert csv.columns.tolist() == pq.read_schema(parquet_path(config, "ACT")).names
    assert csv["gnaf_address_detail_pids"].tolist() == ["GA1|GA2", ""]


def test_only_the_published_files_land_in_out_dir(config):
    stage(config)
    publish_state(config, None, "ACT", SOURCE)
    assert sorted(p.name for p in config.out_dir.iterdir()) == ["ACT_parcels.csv", "ACT_parcels.parquet"]
    assert not list(config.staging_dir.glob("*.tmp"))


def test_missing_staged_csv(config):
    assert publish_state(config, None, "ACT", SOURCE) is None
    assert not parquet_path(config, "ACT").exists()
