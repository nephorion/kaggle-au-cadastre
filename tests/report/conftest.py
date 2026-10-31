import datetime as dt

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from cadastre_gnaf.storage import parquet_path, write_progress

WKT = "POLYGON ((149.000001 -35.000001,149.000001 -34.000001,150.000001 -34.000001,149.000001 -35.000001))"
PARCELS = pa.table({
    "state": ["ACT", "ACT"],
    "source_oid": pa.array([1, 2], pa.int64()),
    "key_dist_blk": pa.array([None, None], pa.string()),
    "gnaf_key_matched": [True, False],
    "gnaf_address_detail_pids": pa.array([["GAACT1", "GAACT2"], None], pa.list_(pa.string())),
    "point_lon": [149.5, 150.5],
    "point_lat": [-34.5, -34.5],
    "OBJECTID": pa.array([1, 2], pa.int64()),
    "ADDRESSES": ["1 A ST\n2 A ST", None],
    "LAST_UPDATE": pa.array([dt.date(2026, 1, 2), None], pa.date32()),
    "wkt": [WKT, None],
})
SUMMARY = ("state,source,features_expected,parcels_written,parcels_matching_gnaf_key,gnaf_addresses,"
           "address_link_rate,key_match_by_candidate,licence\n"
           "ACT,http://act,2.0,2.0,1.0,4.0,0.5,,(c) ACT\n")
FIELDS = [{"name": "OBJECTID", "alias": "OBJECTID", "type": "esriFieldTypeOID"},
          {"name": "ADDRESSES", "alias": "Street addresses", "type": "esriFieldTypeString"},
          {"name": "LAST_UPDATE", "alias": "", "type": "esriFieldTypeDate"}]


@pytest.fixture
def dataset_out(config):
    """An output folder holding a published ACT parcels file, summary.csv and ATTRIBUTION.md."""
    out = config.out_dir
    out.mkdir(parents=True)
    parquet_path(config, "ACT").parent.mkdir()
    pq.write_table(PARCELS, parquet_path(config, "ACT"))
    (out / "summary.csv").write_text(SUMMARY, encoding="utf-8", newline="")
    (out / "ATTRIBUTION.md").write_text("# Data sources and licences\n\n- **ACT**: (c) ACT. Source: http://act\n"
                                        "\nBuilt 2026-10-30T09:00.\n", encoding="utf-8", newline="")
    write_progress(config, "ACT", {"done": True, "fields": FIELDS})
    return config
