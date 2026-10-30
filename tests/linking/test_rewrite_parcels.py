import pandas as pd

from cadastre_gnaf.linking import rewrite_parcels


def test_inserts_gnaf_columns_after_keys_and_deduplicates(act_parcels):
    chosen = pd.Series({"1": "CANB/BRAD/18/41", "2": "CANB/BRAD/18/99"})
    matched = pd.Series({"1": True, "2": False})
    counts = pd.Series({"1": 2})
    rewrite_parcels(act_parcels, 2, chosen, matched, counts, chunk=1)      # chunk=1: dedupe across chunks
    df = pd.read_csv(act_parcels, dtype=str)
    assert df["source_oid"].tolist() == ["1", "2"]
    assert list(df.columns[:7]) == ["state", "source_oid", "key_dist_div_sec_blk", "key_dist_blk",
                                    "gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count"]
    assert df["gnaf_key_matched"].tolist() == ["True", "False"]
    assert df["gnaf_address_count"].tolist() == ["2", "0"]
    assert not act_parcels.with_name(act_parcels.name + ".tmp").exists()


def test_rerun_replaces_existing_gnaf_columns(act_parcels):
    rewrite_parcels(act_parcels, 2, pd.Series({"1": "A"}), pd.Series({"1": True}), pd.Series(dtype=int))
    rewrite_parcels(act_parcels, 2, pd.Series({"1": "B"}), pd.Series({"1": False}), pd.Series(dtype=int))
    df = pd.read_csv(act_parcels, dtype=str, keep_default_na=False)
    assert df.columns.tolist().count("gnaf_legal_parcel_id") == 1
    assert df["gnaf_legal_parcel_id"].tolist() == ["B", ""]
