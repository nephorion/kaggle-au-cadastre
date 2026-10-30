import importlib
from dataclasses import replace

from cadastre_gnaf.linking import run_gnaf
from cadastre_gnaf.sources import Source

mod = importlib.import_module("cadastre_gnaf.linking.run_gnaf")

SOURCES = {s: Source(url=None, keys=dict, licence="l") for s in ("A", "B", "C")}


def test_collects_summaries_and_survives_failures(config, monkeypatch):
    def fake_finalise(cfg, gnaf, state, source):
        if state == "B":
            raise RuntimeError("bad")
        return {"state": state} if state == "A" else None

    monkeypatch.setattr(mod, "finalise_state", fake_finalise)
    result = run_gnaf(replace(config, states=("A", "B", "C")), None, SOURCES, gnaf=object())
    assert result == [{"state": "A"}]


def test_opens_gnaf_when_not_given(config, monkeypatch):
    opened = []
    monkeypatch.setattr(mod, "open_gnaf", lambda cfg, session: opened.append(1) or "G")
    monkeypatch.setattr(mod, "finalise_state", lambda cfg, gnaf, st, src: {"state": st, "gnaf": gnaf})
    assert run_gnaf(replace(config, states=("A",)), None, SOURCES) == [{"state": "A", "gnaf": "G"}]
    assert opened == [1]
