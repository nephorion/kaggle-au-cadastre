import importlib
from dataclasses import replace

from cadastre_gnaf.download import run_downloads
from cadastre_gnaf.sources import Source

mod = importlib.import_module("cadastre_gnaf.download.run_downloads")

SOURCES = {
    "WEB": Source(url="http://web", keys=dict, licence="l"),
    "LOCAL": Source(url=None, keys=dict, licence="l"),
    "NONE": Source(url=None, keys=dict, licence="l"),
    "BAD": Source(url="http://bad", keys=dict, licence="l"),
}


def test_dispatches_per_state_and_collects_failures(config, monkeypatch):
    calls = []

    def fake_download(cfg, session, state, source):
        if state == "BAD":
            raise RuntimeError("boom")
        calls.append(("web", state))

    monkeypatch.setattr(mod, "download_arcgis_state", fake_download)
    monkeypatch.setattr(mod, "load_local_state", lambda cfg, st, src, path: calls.append(("local", st, path)))
    cfg = replace(config, states=("WEB", "LOCAL", "NONE", "BAD"), local_sources={"LOCAL": "/x.shp"})

    failures = run_downloads(cfg, session=None, sources=SOURCES)

    assert calls == [("web", "WEB"), ("local", "LOCAL", "/x.shp")]
    assert failures == {"BAD": "RuntimeError('boom')"}


def test_local_file_overrides_web_service(config, monkeypatch):
    calls = []
    monkeypatch.setattr(mod, "download_arcgis_state", lambda *a: calls.append("web"))
    monkeypatch.setattr(mod, "load_local_state", lambda *a: calls.append("local"))
    run_downloads(replace(config, states=("WEB",), local_sources={"WEB": "f"}), None, SOURCES)
    assert calls == ["local"]
