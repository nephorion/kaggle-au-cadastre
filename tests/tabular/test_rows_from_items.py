from cadastre_gnaf.keys import keys_act
from cadastre_gnaf.tabular import rows_from_items

ATTRS = {"OBJECTID": 7, "DISTRICT_SHORT": "CANB", "BLOCK_NUMBER": 3, "UPDATED": 0, "state": "act"}


def test_builds_row_with_keys_point_attrs_and_wkt():
    [row] = rows_from_items("ACT", keys_act, [(ATTRS, "POINT (1 2)", 1.0, 2.0)], {"UPDATED"}, "OBJECTID")
    assert row["state"] == "ACT" and row["source_oid"] == 7
    assert row["key_dist_blk"] == "CANB/3"
    assert (row["point_lon"], row["point_lat"]) == (1.0, 2.0)
    assert row["UPDATED"] == "1970-01-01"                  # date field converted
    assert row["src_state"] == "act"                       # clashing name prefixed
    assert row["wkt"] == "POINT (1 2)"


def test_without_wkt():
    [row] = rows_from_items("ACT", keys_act, [(ATTRS, "POINT (1 2)", 1, 2)], set(), "OBJECTID", include_wkt=False)
    assert "wkt" not in row and row["UPDATED"] == 0
