from cadastre_gnaf.arcgis import oid_bounds


def test_bounds_from_statistics(arcgis_layer, square_feature):
    s = arcgis_layer([square_feature(i) for i in (5, 9, 30)])
    assert oid_bounds(s, "http://x", "OBJECTID") == (5, 30)
    assert len(s.calls) == 1


def test_at_least_restricts_minimum(arcgis_layer, square_feature):
    s = arcgis_layer([square_feature(i) for i in (5, 9, 30)])
    assert oid_bounds(s, "http://x", "OBJECTID", at_least=10) == (30, 30)
    assert "OBJECTID >= 10" in s.calls[0][2]["where"]


def test_falls_back_to_id_list_when_statistics_unsupported(fake_session, fake_response):
    def handler(m, u, p):
        if "outStatistics" in p:
            return fake_response({"features": []})          # IndexError -> fallback
        return fake_response({"objectIds": [7, 3, 11]})
    assert oid_bounds(fake_session(handler), "http://x", "OBJECTID") == (3, 11)


def test_empty_layer(fake_session, fake_response):
    def handler(m, u, p):
        if "outStatistics" in p:
            return fake_response({"features": [{"attributes": None}]})   # AttributeError -> fallback
        return fake_response({"objectIds": None})
    assert oid_bounds(fake_session(handler), "http://x", "OBJECTID") == (None, None)
