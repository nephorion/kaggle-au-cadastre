from dataclasses import replace

import pandas as pd
import pytest

from cadastre_gnaf.keys import keys_act
from cadastre_gnaf.linking import finalise_state
from cadastre_gnaf.sources import Source
from cadastre_gnaf.storage import read_progress, write_progress

SOURCE = Source(url="http://x", keys=keys_act, licence="l")


@pytest.fixture
def no_spatial(config):
    return replace(config, spatial_join_states=())


def test_missing_parcels_file(no_spatial, gnaf):
    assert finalise_state(no_spatial, gnaf, "ACT", SOURCE) is None


def test_key_matching(no_spatial, gnaf, act_parcels):
    summ = finalise_state(no_spatial, gnaf, "ACT", SOURCE)
    assert summ == {"state": "ACT", "parcels": 2,
                    "key_match": {"key_dist_div_sec_blk": "1/2", "key_dist_blk": "0/2"},
                    "gnaf_addresses": 4, "addresses_linked": 2, "address_link_rate": 0.5,
                    "parcels_with_gnaf_key_match": 1}
    parcels = pd.read_csv(act_parcels, dtype=str, keep_default_na=False).set_index("source_oid")
    assert parcels.loc["1", "gnaf_legal_parcel_id"] == "CANB/BRAD/18/41"
    assert parcels.loc["1", "gnaf_address_count"] == "2"
    assert parcels.loc["1", "gnaf_address_detail_pids"] == "GAACT1|GAACT2"
    assert parcels.loc["1", "gnaf_link_methods"] == "legal_parcel_id"
    assert parcels.loc["2", "gnaf_key_matched"] == "False"
    assert parcels.loc["2", "gnaf_address_detail_pids"] == ""
    assert not list(no_spatial.out_dir.glob("*links*"))


def test_spatial_join_links_remaining_addresses(config, gnaf, act_parcels):
    pytest.importorskip("geopandas")
    summ = finalise_state(replace(config, spatial_join_states=("ACT",)), gnaf, "ACT", SOURCE)
    assert summ["addresses_linked"] == 4 and summ["address_link_rate"] == 1.0
    parcels = pd.read_csv(act_parcels, dtype=str).set_index("source_oid")
    assert parcels["gnaf_address_count"].to_dict() == {"1": "3", "2": "1"}
    assert parcels.loc["1", "gnaf_link_methods"] == "legal_parcel_id|spatial_within"
    assert parcels.loc["2", "gnaf_address_detail_pids"] == "GAACT3"


def test_without_gnaf_fills_best_key(no_spatial, act_parcels):
    summ = finalise_state(no_spatial, None, "ACT", SOURCE)
    assert summ == {"state": "ACT", "parcels": 2}
    parcels = pd.read_csv(act_parcels, dtype=str)
    assert parcels["gnaf_legal_parcel_id"].tolist() == ["CANB/BRAD/18/41", "CANB/BRAD/18/99"]
    assert set(parcels["gnaf_address_count"]) == {"0"}
    assert parcels["gnaf_address_detail_pids"].isna().all()


def test_saves_summary_in_progress(no_spatial, gnaf, act_parcels):
    write_progress(no_spatial, "ACT", {"done": True, "rows": 3})
    summ = finalise_state(no_spatial, gnaf, "ACT", SOURCE)
    prog = read_progress(no_spatial, "ACT")
    assert prog["gnaf"] == summ and prog["done"] and prog["rows"] == 3


def test_stacked_polygons_share_a_group_and_one_gets_the_addresses(config, gnaf, act_parcels):
    pytest.importorskip("geopandas")
    df = pd.read_csv(act_parcels, dtype=str)
    stacked = df.iloc[[1]].assign(source_oid="3")              # OID 3: same polygon as OID 2
    pd.concat([df, stacked]).to_csv(act_parcels, index=False)
    finalise_state(replace(config, spatial_join_states=("ACT",)), gnaf, "ACT", SOURCE)
    parcels = pd.read_csv(act_parcels, dtype=str, keep_default_na=False).set_index("source_oid")
    assert parcels.loc[["2", "3"], "geometry_group_id"].tolist() == ["2", "2"]
    assert parcels.loc[["2", "3"], "geometry_group_size"].tolist() == ["2", "2"]
    assert parcels.loc["2", "gnaf_address_detail_pids"] == "GAACT3"
    assert parcels.loc["3", "gnaf_address_detail_pids"] == ""
    assert parcels.loc["1", "geometry_group_size"] == "1"
