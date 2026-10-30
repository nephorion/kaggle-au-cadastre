import pytest

from cadastre_gnaf.storage import write_progress

PARCELS = (
    "state,source_oid,key_dist_div_sec_blk,key_dist_blk,gnaf_legal_parcel_id,gnaf_key_matched,"
    "gnaf_address_count,point_lon,point_lat,OBJECTID,ADDRESSES,LAST_UPDATE,EXTRA,wkt\n"
    'ACT,1,CANB/BRAD/18/41,,CANB/BRAD/18/41,True,2,149.5,-34.5,1,"1 A ST\n2 A ST",2026-01-02,7,'
    '"POLYGON ((149.000001 -35.000001,149.000001 -34.000001,150.000001 -34.000001,149.000001 -35.000001))"\n'
    "ACT,2,,,,False,0,150.5,-34.5,2,,,8,\n"
)
LINKS = "address_detail_pid,legal_parcel_id,source_oid,method\nGAACT1,CANB/BRAD/18/41,1,legal_parcel_id\n"
SUMMARY = ("state,source,features_expected,parcels_written,parcels_matching_gnaf_key,gnaf_addresses,"
           "address_link_rate,key_match_by_candidate,licence\n"
           "ACT,http://act,2.0,2.0,1.0,4.0,0.5,,(c) ACT\n")
FIELDS = [{"name": "OBJECTID", "alias": "OBJECTID", "type": "esriFieldTypeOID"},
          {"name": "ADDRESSES", "alias": "Street addresses", "type": "esriFieldTypeString"},
          {"name": "LAST_UPDATE", "alias": "", "type": "esriFieldTypeDate"}]


@pytest.fixture
def dataset_out(config):
    """An output folder holding a finished ACT state, summary.csv and ATTRIBUTION.md."""
    out = config.out_dir
    out.mkdir(parents=True)
    (out / "ACT_parcels.csv").write_text(PARCELS, encoding="utf-8", newline="")
    (out / "ACT_gnaf_address_parcel_links.csv").write_text(LINKS, encoding="utf-8", newline="")
    (out / "summary.csv").write_text(SUMMARY, encoding="utf-8", newline="")
    (out / "ATTRIBUTION.md").write_text("# Data sources and licences\n\n- **ACT**: (c) ACT. Source: http://act\n"
                                        "\nBuilt 2026-10-30T09:00.\n", encoding="utf-8", newline="")
    write_progress(config, "ACT", {"done": True, "fields": FIELDS})
    return config
