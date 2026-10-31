import pytest
import requests

from cadastre_gnaf.arcgis import ArcGISError, arcgis_get


def no_sleep(_):
    pass


def test_adds_json_format_and_returns_payload(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({"ok": 1}))
    assert arcgis_get(s, "http://x", {"a": 1}, sleep=no_sleep) == {"ok": 1}
    assert s.calls == [("GET", "http://x", {"f": "json", "a": 1})]


def test_long_queries_use_post(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({}))
    arcgis_get(s, "http://x", {"where": "x" * 2000}, sleep=no_sleep)
    assert s.calls[0][0] == "POST"


def test_token_requests_use_post(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({}))
    arcgis_get(s, "http://x", {"token": "secret"}, sleep=no_sleep)
    assert s.calls[0][0] == "POST"


def test_token_is_redacted_from_final_error(fake_session):
    s = fake_session(lambda m, u, p: requests.ConnectionError("http://x?token=secret refused"))
    with pytest.raises(ArcGISError) as e:
        arcgis_get(s, "http://x", {"token": "secret"}, retries=2, sleep=no_sleep)
    assert "secret" not in str(e.value) and "<token>" in str(e.value)


def test_retries_transient_errors_then_succeeds(fake_session, fake_response):
    responses = iter([fake_response({}, status_code=503), requests.ConnectionError("down"),
                      fake_response({"error": {"code": 500}}), fake_response({"ok": 1})])
    sleeps = []
    s = fake_session(lambda m, u, p: next(responses))
    assert arcgis_get(s, "http://x", {}, sleep=sleeps.append) == {"ok": 1}
    assert len(s.calls) == 4 and len(sleeps) == 3
    assert sleeps[0] < sleeps[1] < sleeps[2]            # exponential backoff


def test_invalid_json_is_retried(fake_session, fake_response):
    responses = iter([fake_response(ValueError("bad json")), fake_response({"ok": 1})])
    s = fake_session(lambda m, u, p: next(responses))
    assert arcgis_get(s, "http://x", {}, sleep=no_sleep) == {"ok": 1}


def test_gives_up_after_retries(fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response({}, status_code=500))
    with pytest.raises(ArcGISError, match="failed after 3 tries"):
        arcgis_get(s, "http://x", {}, retries=3, sleep=no_sleep)
    assert len(s.calls) == 3


def test_backoff_capped_at_60s(fake_session, fake_response):
    sleeps = []
    s = fake_session(lambda m, u, p: fake_response({}, status_code=429))
    with pytest.raises(ArcGISError):
        arcgis_get(s, "http://x", {}, retries=8, sleep=sleeps.append)
    assert max(sleeps) == 60
