import pandas as pd

from cadastre_gnaf.linking import geometry_groups

SQUARE = "POLYGON ((0 0,0 1,1 1,1 0,0 0))"
OTHER = "POLYGON ((5 5,5 6,6 6,6 5,5 5))"


def write(tmp_path, oids, wkts):
    path = tmp_path / "p.csv"
    pd.DataFrame({"source_oid": oids, "wkt": wkts}).to_csv(path, index=False)
    return path


def test_identical_polygons_share_the_lowest_oid(tmp_path):
    g = geometry_groups(write(tmp_path, [30, 4, 10, 7], [SQUARE, SQUARE, OTHER, SQUARE]), chunk=2)
    assert g.loc["30"].tolist() == ["4", 3] and g.loc["4"].tolist() == ["4", 3] and g.loc["7"].tolist() == ["4", 3]
    assert g.loc["10"].tolist() == ["10", 1]


def test_numeric_not_text_order(tmp_path):
    g = geometry_groups(write(tmp_path, [10, 9], [SQUARE, SQUARE]))
    assert g.loc["10", "geometry_group_id"] == "9"


def test_blank_wkt_is_never_grouped(tmp_path):
    g = geometry_groups(write(tmp_path, [1, 2], ["", ""]))
    assert g["geometry_group_id"].to_dict() == {"1": "1", "2": "2"}


def test_duplicate_rows_counted_once(tmp_path):
    g = geometry_groups(write(tmp_path, [1, 1, 2], [SQUARE, SQUARE, SQUARE]))
    assert g.loc["2"].tolist() == ["1", 2] and len(g) == 2


def test_no_wkt_column(tmp_path):
    path = tmp_path / "p.csv"
    pd.DataFrame({"source_oid": [1]}).to_csv(path, index=False)
    assert geometry_groups(path) is None
