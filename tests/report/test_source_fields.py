from cadastre_gnaf.report import source_fields
from cadastre_gnaf.sources import Source
from cadastre_gnaf.storage import write_progress

SOURCE = Source(url="http://layer", keys=dict, licence="x")
FIELD = {"name": "BLOCK", "alias": "Block", "type": "esriFieldTypeString"}


def test_uses_fields_saved_at_download(config, fake_session):
    write_progress(config, "ACT", {"fields": [FIELD]})
    session = fake_session(lambda *a: AssertionError("no request expected"))
    assert source_fields(config, session, "ACT", SOURCE) == {"BLOCK": FIELD}
    assert session.calls == []


def test_asks_the_service_when_not_saved(config, arcgis_layer):
    fields = source_fields(config, arcgis_layer([]), "ACT", SOURCE)
    assert set(fields) == {"OBJECTID", "BLOCK", "SHAPE"}


def test_offline_or_failing_service_gives_empty(config, fake_session, capsys):
    assert source_fields(config, None, "ACT", SOURCE) == {}
    # an error arcgis_get does not retry, so the test does not sleep
    assert source_fields(config, fake_session(lambda *a: RuntimeError("down")), "ACT", SOURCE) == {}
    assert "could not read field metadata" in capsys.readouterr().out


def test_local_source_without_url(config, arcgis_layer):
    assert source_fields(config, arcgis_layer([]), "ACT", Source(url=None, keys=dict, licence="x")) == {}
