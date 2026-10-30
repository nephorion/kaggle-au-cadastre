import pandas as pd

from cadastre_gnaf.constants import LEADING_COLUMNS
from cadastre_gnaf.linking import rewrite_parcels

NO_LINKS = pd.DataFrame(columns=["address_detail_pid", "source_oid", "method"], dtype=str)


def test_adds_gnaf_columns_and_deduplicates(act_parcels):
    chosen = pd.Series({"1": "CANB/BRAD/18/41", "2": "CANB/BRAD/18/99"})
    matched = pd.Series({"1": True, "2": False})
    links = pd.DataFrame({"address_detail_pid": ["GA2", "GA1", "GA1"], "source_oid": ["1", "1", "1"],
                          "method": ["spatial_within", "legal_parcel_id", "legal_parcel_id"]})
    rewrite_parcels(act_parcels, chosen, matched, links, chunk=1)      # chunk=1: dedupe across chunks
    df = pd.read_csv(act_parcels, dtype=str, keep_default_na=False)
    assert df["source_oid"].tolist() == ["1", "2"]
    assert df["gnaf_key_matched"].tolist() == ["True", "False"]
    assert df["gnaf_address_count"].tolist() == ["2", "0"]
    assert df["gnaf_address_detail_pids"].tolist() == ["GA1|GA2", ""]
    assert df["gnaf_link_methods"].tolist() == ["legal_parcel_id|spatial_within", ""]
    assert not act_parcels.with_name(act_parcels.name + ".tmp").exists()


def test_shared_column_order(act_parcels):
    rewrite_parcels(act_parcels, pd.Series(dtype=str), pd.Series(dtype=bool), NO_LINKS)
    cols = pd.read_csv(act_parcels, nrows=0).columns.tolist()
    assert cols[:len(LEADING_COLUMNS)] == list(LEADING_COLUMNS)
    assert cols[len(LEADING_COLUMNS):] == ["key_dist_div_sec_blk", "key_dist_blk", "BLOCK", "wkt"]


def test_geometry_groups(act_parcels):
    groups = pd.DataFrame({"geometry_group_id": ["1"], "geometry_group_size": [2]}, index=["2"])
    rewrite_parcels(act_parcels, pd.Series(dtype=str), pd.Series(dtype=bool), NO_LINKS, groups)
    df = pd.read_csv(act_parcels, dtype=str)
    assert df["geometry_group_id"].tolist() == ["1", "1"]                # OID 1 not in groups: its own group
    assert df["geometry_group_size"].tolist() == ["1", "2"]


def test_without_groups_each_parcel_is_its_own_group(act_parcels):
    rewrite_parcels(act_parcels, pd.Series(dtype=str), pd.Series(dtype=bool), NO_LINKS)
    df = pd.read_csv(act_parcels, dtype=str)
    assert df["geometry_group_id"].tolist() == df["source_oid"].tolist()
    assert set(df["geometry_group_size"]) == {"1"}


def test_rerun_replaces_existing_columns(act_parcels):
    links = pd.DataFrame({"address_detail_pid": ["GA1"], "source_oid": ["1"], "method": ["legal_parcel_id"]})
    rewrite_parcels(act_parcels, pd.Series({"1": "A"}), pd.Series({"1": True}), links)
    rewrite_parcels(act_parcels, pd.Series({"1": "B"}), pd.Series({"1": False}), NO_LINKS)
    df = pd.read_csv(act_parcels, dtype=str, keep_default_na=False)
    for col in ("gnaf_legal_parcel_id", "gnaf_address_detail_pids", "geometry_group_id"):
        assert df.columns.tolist().count(col) == 1
    assert df["gnaf_legal_parcel_id"].tolist() == ["B", ""]
    assert df["gnaf_address_detail_pids"].tolist() == ["", ""]
