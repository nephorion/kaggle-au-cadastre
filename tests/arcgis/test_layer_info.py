import pytest

from cadastre_gnaf.arcgis import ArcGISError, layer_info


def test_uses_object_id_field(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({"objectIdField": "FID", "fields": []}))
    info, oid = layer_info(s, "http://x")
    assert oid == "FID" and info["objectIdField"] == "FID"


def test_falls_back_to_oid_typed_field(fake_session, fake_response):
    fields = [{"name": "A", "type": "esriFieldTypeString"}, {"name": "OID_", "type": "esriFieldTypeOID"}]
    s = fake_session(lambda m, u, p: fake_response({"fields": fields}))
    assert layer_info(s, "http://x")[1] == "OID_"


def test_raises_without_oid(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({"fields": []}))
    with pytest.raises(ArcGISError, match="No ObjectID"):
        layer_info(s, "http://x")


def test_passes_token(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({"objectIdField": "OBJECTID"}))
    layer_info(s, "http://x", token="t")
    assert s.calls[0][2]["token"] == "t"
