from cadastre_gnaf.arcgis import fetch_range


def oids(features):
    return [f["attributes"]["OBJECTID"] for f in features]


def test_returns_features_in_half_open_range(arcgis_layer, square_feature):
    s = arcgis_layer([square_feature(i) for i in range(1, 11)])
    assert oids(fetch_range(s, "http://x", "OBJECTID", 3, 6)) == [3, 4, 5]


def test_query_parameters(arcgis_layer, square_feature):
    s = arcgis_layer([square_feature(1)])
    fetch_range(s, "http://x", "OBJECTID", 0, 5, where="A=1", token="t", decimals=4)
    p = s.calls[0][2]
    assert p["where"] == "(A=1) AND OBJECTID >= 0 AND OBJECTID < 5"
    assert p["outSR"] == 4326 and p["geometryPrecision"] == 5 and p["token"] == "t"


def test_splits_range_when_server_truncates(arcgis_layer, square_feature):
    s = arcgis_layer([square_feature(i) for i in range(1, 11)], max_records=3)
    assert oids(fetch_range(s, "http://x", "OBJECTID", 1, 11)) == list(range(1, 11))
    assert len(s.calls) > 1
