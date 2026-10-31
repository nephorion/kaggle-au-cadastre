from cadastre_gnaf.arcgis import feature_count


def test_counts_matching_features(arcgis_layer, square_feature):
    s = arcgis_layer([square_feature(i) for i in (1, 2, 3)])
    assert feature_count(s, "http://x") == 3
    assert s.calls[0][1] == "http://x/query"


def test_missing_count_is_zero(fake_session, fake_response):
    assert feature_count(fake_session(lambda m, u, p: fake_response({})), "http://x") == 0


def test_passes_where_and_token(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({"count": 1}))
    feature_count(s, "http://x", where="A=1", token="t")
    assert s.calls[0][2]["where"] == "A=1" and s.calls[0][2]["token"] == "t"
