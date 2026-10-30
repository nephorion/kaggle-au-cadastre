import pandas as pd

from cadastre_gnaf.linking import rewrite_parcels

NO_LINKS = pd.DataFrame(columns=["address_detail_pid", "source_oid", "method"], dtype=str)


def test_inserts_gnaf_columns_after_keys_and_deduplicates(act_parcels):
    chosen = pd.Series({"1": "CANB/BRAD/18/41", "2": "CANB/BRAD/18/99"})
    matched = pd.Series({"1": True, "2": False})
    links = pd.DataFrame({"address_detail_pid": ["GA2", "GA1", "GA1"], "source_oid": ["1", "1", "1"],
                          "method": ["spatial_within", "legal_parcel_id", "legal_parcel_id"]})
    rewrite_parcels(act_parcels, 2, chosen, matched, links, chunk=1)      # chunk=1: dedupe across chunks
    df = pd.read_csv(act_parcels, dtype=str, keep_default_na=False)
    assert df["source_oid"].tolist() == ["1", "2"]
    assert list(df.columns[:9]) == ["state", "source_oid", "key_dist_div_sec_blk", "key_dist_blk",
                                    "gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count",
                                    "gnaf_address_detail_pids", "gnaf_link_methods"]
    assert df["gnaf_key_matched"].tolist() == ["True", "False"]
    assert df["gnaf_address_count"].tolist() == ["2", "0"]
    assert df["gnaf_address_detail_pids"].tolist() == ["GA1|GA2", ""]
    assert df["gnaf_link_methods"].tolist() == ["legal_parcel_id|spatial_within", ""]
    assert not act_parcels.with_name(act_parcels.name + ".tmp").exists()


def test_rerun_replaces_existing_gnaf_columns(act_parcels):
    links = pd.DataFrame({"address_detail_pid": ["GA1"], "source_oid": ["1"], "method": ["legal_parcel_id"]})
    rewrite_parcels(act_parcels, 2, pd.Series({"1": "A"}), pd.Series({"1": True}), links)
    rewrite_parcels(act_parcels, 2, pd.Series({"1": "B"}), pd.Series({"1": False}), NO_LINKS)
    df = pd.read_csv(act_parcels, dtype=str, keep_default_na=False)
    assert df.columns.tolist().count("gnaf_legal_parcel_id") == 1
    assert df.columns.tolist().count("gnaf_address_detail_pids") == 1
    assert df["gnaf_legal_parcel_id"].tolist() == ["B", ""]
    assert df["gnaf_address_detail_pids"].tolist() == ["", ""]
