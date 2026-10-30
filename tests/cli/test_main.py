import importlib

import pytest

from cadastre_gnaf.cli import main

mod = importlib.import_module("cadastre_gnaf.cli.main")


@pytest.fixture
def calls(monkeypatch):
    calls = []
    monkeypatch.setattr(mod, "make_session", lambda: "session")
    monkeypatch.setattr(mod, "run_downloads", lambda cfg, s: calls.append("download") or {})
    monkeypatch.setattr(mod, "run_gnaf", lambda cfg, s: calls.append("gnaf") or [{"state": "ACT"}])
    monkeypatch.setattr(mod, "write_summary", lambda cfg, summaries: calls.append(("summary", summaries)))
    return calls


def args(tmp_path, *extra):
    return ["--out", str(tmp_path / "o"), "--work", str(tmp_path / "w"), *extra]


def test_runs_all_steps_and_creates_folders(tmp_path, calls):
    assert main(args(tmp_path)) == 0
    assert calls == ["download", "gnaf", ("summary", [{"state": "ACT"}])]
    assert (tmp_path / "o").is_dir() and (tmp_path / "w").is_dir()


@pytest.mark.parametrize(("step", "expected"), [("download", ["download"]), ("gnaf", ["gnaf"])])
def test_single_step(tmp_path, calls, step, expected):
    main(args(tmp_path, "--step", step))
    assert [c for c in calls if isinstance(c, str)] == expected


def test_exit_code_reflects_failures(tmp_path, calls, monkeypatch):
    monkeypatch.setattr(mod, "run_downloads", lambda cfg, s: {"NSW": "boom"})
    assert main(args(tmp_path, "--step", "download")) == 1
