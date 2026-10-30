from cadastre_gnaf.tabular import features_to_items


def test_converts_geometry(square_feature):
    [(attrs, wkt, lon, lat)] = features_to_items([square_feature(1, x=0, y=0, BLOCK="7")])
    assert attrs == {"OBJECTID": 1, "BLOCK": "7"}
    assert wkt == "POLYGON ((0 0,0 1,1 1,1 0,0 0))"
    assert (lon, lat) == (0.5, 0.5)


def test_feature_without_geometry_or_attributes():
    assert features_to_items([{}]) == [({}, "", None, None)]
