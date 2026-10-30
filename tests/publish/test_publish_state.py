import datetime as dt

import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.publish import publish_state
from cadastre_gnaf.sources import Source
from cadastre_gnaf.storage import parcels_path, parquet_path, write_progress

SOURCE = Source(url="http://x", keys=dict, licence="l")
CSV = ("state,source_oid,key_dist_blk,gnaf_legal_parcel_id,gnaf_key_matched,gnaf_address_count,"
       "gnaf_address_detail_pids,gnaf_link_methods,point_lon,point_lat,BLOCK,EDITED,wkt\n"
       "ACT,1,CANB/1,CANB/1,True,2,GA1|GA2,legal_parcel_id,149.5,-35.5,0041,2026-01-02,POLYGON EMPTY\n"
       "ACT,2,,,False,0,,,150.5,-35.5,,,\n")


def test_publishes_typed_parquet(config, capsys):
    staged = parcels_path(config, "ACT")
    staged.parent.mkdir(parents=True)
    staged.write_text(CSV)
    write_progress(config, "ACT", {"fields": [{"name": "BLOCK", "type": "esriFieldTypeString"},
                                              {"name": "EDITED", "type": "esriFieldTypeDate"}]})
    assert publish_state(config, None, "ACT", SOURCE) == 2
    t = pq.read_table(parquet_path(config, "ACT"))
    types = {f.name: f.type for f in t.schema}
    assert types["source_oid"] == pa.int64() and types["gnaf_key_matched"] == pa.bool_()
    assert types["point_lon"] == pa.float64() and types["EDITED"] == pa.date32()
    assert types["gnaf_address_detail_pids"] == pa.list_(pa.string())
    row = t.to_pylist()[0]
    assert row["BLOCK"] == "0041"                                    # string field keeps leading zeros
    assert row["EDITED"] == dt.date(2026, 1, 2)
    assert row["gnaf_address_detail_pids"] == ["GA1", "GA2"]
    assert t.to_pylist()[1]["gnaf_address_detail_pids"] is None
    assert "published 2 parcels -> ACT_parcels.parquet" in capsys.readouterr().out


def test_missing_staged_csv(config):
    assert publish_state(config, None, "ACT", SOURCE) is None
    assert not parquet_path(config, "ACT").exists()


def test_only_the_published_files_land_in_out_dir(config):
    staged = parcels_path(config, "ACT")
    staged.parent.mkdir(parents=True)
    staged.write_text(CSV)
    publish_state(config, None, "ACT", SOURCE)
    assert sorted(p.name for p in config.out_dir.iterdir()) == ["ACT_parcels.csv", "ACT_parcels.parquet"]
    assert (config.out_dir / "ACT_parcels.csv").read_text() == CSV
    assert not list(config.staging_dir.glob("*.tmp"))
