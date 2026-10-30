import pandas as pd
import pytest

from cadastre_gnaf.linking import spatial_links

pytest.importorskip("geopandas")

POINTS = pd.DataFrame({"ADDRESS_DETAIL_PID": ["IN1", "IN2", "OUT"],
                       "LONGITUDE": [149.5, 150.5, 160.0], "LATITUDE": [-34.5, -34.5, -34.5]})


def test_points_joined_to_containing_parcels(act_parcels):
    links = spatial_links(act_parcels, POINTS, chunk=2)       # chunking across points
    pairs = set(zip(links["address_detail_pid"], links["source_oid"]))
    assert pairs == {("IN1", 1), ("IN2", 2)}                   # one parcel per address
    assert "OUT" not in set(links["address_detail_pid"])


def test_invalid_polygons_repaired_and_blank_wkt_skipped(tmp_path):
    path = tmp_path / "p.csv"
    bowtie = "POLYGON ((0 0,2 2,2 0,0 2,0 0))"                 # self-intersecting
    pd.DataFrame({"source_oid": [1, 2], "wkt": [bowtie, ""]}).to_csv(path, index=False)
    points = pd.DataFrame({"ADDRESS_DETAIL_PID": ["A"], "LONGITUDE": [1.8], "LATITUDE": [1.0]})
    assert spatial_links(path, points)["source_oid"].tolist() == [1]


def test_no_points(act_parcels):
    links = spatial_links(act_parcels, POINTS.iloc[0:0])
    assert links.empty and list(links.columns) == ["address_detail_pid", "source_oid"]


def test_smallest_containing_polygon_wins(tmp_path):
    path = tmp_path / "p.csv"
    big, small = "POLYGON ((0 0,0 10,10 10,10 0,0 0))", "POLYGON ((1 1,1 2,2 2,2 1,1 1))"
    pd.DataFrame({"source_oid": [1, 2], "wkt": [big, small]}).to_csv(path, index=False)
    points = pd.DataFrame({"ADDRESS_DETAIL_PID": ["IN_SMALL", "BIG_ONLY"], "LONGITUDE": [1.5, 5.0],
                           "LATITUDE": [1.5, 5.0]})
    links = spatial_links(path, points).set_index("address_detail_pid")["source_oid"].to_dict()
    assert links == {"IN_SMALL": 2, "BIG_ONLY": 1}


def test_keep_limits_the_parcels(tmp_path):
    path = tmp_path / "p.csv"
    square = "POLYGON ((0 0,0 1,1 1,1 0,0 0))"
    pd.DataFrame({"source_oid": [1, 2, 3], "wkt": [square] * 3}).to_csv(path, index=False)
    points = pd.DataFrame({"ADDRESS_DETAIL_PID": ["A"], "LONGITUDE": [0.5], "LATITUDE": [0.5]})
    assert spatial_links(path, points, keep={"1"})["source_oid"].tolist() == [1]
