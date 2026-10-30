from dataclasses import replace

import pandas as pd
import pytest

from cadastre_gnaf.download import download_arcgis_state
from cadastre_gnaf.keys import keys_act
from cadastre_gnaf.sources import Source
from cadastre_gnaf.storage import parcels_path, read_progress, write_progress

SOURCE = Source(url="http://layer", keys=keys_act, licence="test")


@pytest.fixture
def small_pages(config):
    return replace(config, page_size=2, workers=2)


def make_features(square_feature, oids):
    return [square_feature(i, x=149 + i, DISTRICT_SHORT="CANB", BLOCK_NUMBER=i, BLOCK=str(i)) for i in oids]


def test_downloads_all_features_across_oid_gaps(small_pages, arcgis_layer, square_feature):
    oids = [1, 2, 3, 4, 5, 100, 101, 102]
    download_arcgis_state(small_pages, arcgis_layer(make_features(square_feature, oids)), "ACT", SOURCE)
    df = pd.read_csv(parcels_path(small_pages, "ACT"))
    assert df["source_oid"].tolist() == oids
    assert list(df.columns[:6]) == ["state", "source_oid", "key_dist_div_sec_blk", "key_dist_blk",
                                    "point_lon", "point_lat"]
    assert df.loc[0, "key_dist_blk"] == "CANB/1"
    assert df.loc[0, "wkt"].startswith("POLYGON ((150 -35")
    prog = read_progress(small_pages, "ACT")
    assert prog["done"] and prog["rows"] == 8 and prog["expected"] == 8


def test_skips_state_already_done(small_pages, arcgis_layer, square_feature):
    download_arcgis_state(small_pages, arcgis_layer(make_features(square_feature, [1])), "ACT", SOURCE)
    again = arcgis_layer(make_features(square_feature, [1]))
    download_arcgis_state(small_pages, again, "ACT", SOURCE)
    assert again.calls == []


def test_force_redownloads(small_pages, arcgis_layer, square_feature):
    download_arcgis_state(small_pages, arcgis_layer(make_features(square_feature, [1])), "ACT", SOURCE)
    forced = replace(small_pages, force=True)
    download_arcgis_state(forced, arcgis_layer(make_features(square_feature, [1, 2])), "ACT", SOURCE)
    assert pd.read_csv(parcels_path(forced, "ACT"))["source_oid"].tolist() == [1, 2]


def test_resumes_from_saved_progress(small_pages, arcgis_layer, square_feature):
    download_arcgis_state(small_pages, arcgis_layer(make_features(square_feature, [1, 2, 3])), "ACT", SOURCE)
    write_progress(small_pages, "ACT", {"next": 4, "rows": 3})        # pretend it stopped after OID 3
    download_arcgis_state(small_pages, arcgis_layer(make_features(square_feature, [1, 2, 3, 4, 5])),
                          "ACT", SOURCE)
    assert pd.read_csv(parcels_path(small_pages, "ACT"))["source_oid"].tolist() == [1, 2, 3, 4, 5]
    assert read_progress(small_pages, "ACT")["rows"] == 5


def test_empty_layer_writes_nothing(small_pages, arcgis_layer):
    download_arcgis_state(small_pages, arcgis_layer([]), "ACT", SOURCE)
    assert not parcels_path(small_pages, "ACT").exists()


def test_token_is_sent(small_pages, arcgis_layer, square_feature):
    cfg = replace(small_pages, arcgis_tokens={"ACT": "secret"})
    session = arcgis_layer(make_features(square_feature, [1]))
    download_arcgis_state(cfg, session, "ACT", SOURCE)
    assert all(params.get("token") == "secret" for _, _, params in session.calls)
