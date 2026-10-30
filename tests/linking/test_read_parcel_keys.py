import pandas as pd

from cadastre_gnaf.linking import read_parcel_keys


def test_indexed_by_oid_deduplicated(act_parcels):
    kd = read_parcel_keys(act_parcels, ["key_dist_div_sec_blk", "key_dist_blk"])
    assert kd.index.tolist() == ["1", "2"]
    assert list(kd.columns) == ["key_dist_div_sec_blk", "key_dist_blk"]
    assert kd.loc["2", "key_dist_blk"] == "CANB/99"


def test_blank_keys_become_nan(tmp_path):
    path = tmp_path / "p.csv"
    path.write_text("source_oid,key_a\n1,\n2,X\n")
    kd = read_parcel_keys(path, ["key_a"])
    assert pd.isna(kd.loc["1", "key_a"]) and kd.loc["2", "key_a"] == "X"
