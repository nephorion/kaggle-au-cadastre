import importlib
from dataclasses import replace

from cadastre_gnaf.publish import run_publish
from cadastre_gnaf.sources import Source

mod = importlib.import_module("cadastre_gnaf.publish.run_publish")

SOURCES = {s: Source(url=None, keys=dict, licence="l") for s in ("A", "B", "C")}


def test_publishes_every_state_and_survives_failures(config, monkeypatch, capsys):
    done = []

    def fake_publish(cfg, session, state, source):
        if state == "B":
            raise RuntimeError("bad")
        done.append(state)

    monkeypatch.setattr(mod, "publish_state", fake_publish)
    run_publish(replace(config, states=("A", "B", "C")), None, SOURCES)
    assert done == ["A", "C"]
    assert "[B] publish FAILED" in capsys.readouterr().out
