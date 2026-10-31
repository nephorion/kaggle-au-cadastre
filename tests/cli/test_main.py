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
    monkeypatch.setattr(mod, "run_publish", lambda cfg, s: calls.append("publish"))
    monkeypatch.setattr(mod, "write_summary", lambda cfg, summaries: calls.append(("summary", summaries)))
    monkeypatch.setattr(mod, "write_dataset_docs", lambda cfg, s: calls.append("docs"))
    return calls


def args(tmp_path, *extra):
    return ["--out", str(tmp_path / "o"), "--work", str(tmp_path / "w"), *extra]


def test_runs_all_steps_and_creates_folders(tmp_path, calls):
    assert main(args(tmp_path)) == 0
    assert calls == ["download", "gnaf", "publish", ("summary", [{"state": "ACT"}]), "docs"]
    assert (tmp_path / "o").is_dir() and (tmp_path / "w").is_dir()


@pytest.mark.parametrize(("step", "expected"), [
    ("download", ["download", "summary", "docs"]),
    ("gnaf", ["gnaf", "publish", "summary", "docs"]),
    ("publish", ["publish", "docs"]),
])
def test_single_step(tmp_path, calls, step, expected):
    main(args(tmp_path, "--step", step))
    assert [c if isinstance(c, str) else c[0] for c in calls] == expected


def test_docs_step_only_rebuilds_docs(tmp_path, calls):
    assert main(args(tmp_path, "--step", "docs")) == 0
    assert calls == ["docs"]


def test_exit_code_reflects_failures(tmp_path, calls, monkeypatch):
    monkeypatch.setattr(mod, "run_downloads", lambda cfg, s: {"NSW": "boom"})
    assert main(args(tmp_path, "--step", "download")) == 1
