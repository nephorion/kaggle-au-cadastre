import pytest

from cadastre_gnaf.constants import GNAF_PACKAGE_ID
from cadastre_gnaf.gnaf import latest_gnaf_zip_url


def package(resources):
    return {"result": {"resources": resources}}


def test_picks_newest_gda2020_zip(fake_session, fake_response):
    resources = [
        {"name": "G-NAF MAY 2026 GDA2020", "url": "http://a/may.zip", "created": "2026-05-15"},
        {"name": "G-NAF AUG 2026 GDA2020", "url": "http://a/aug.zip", "created": "2026-08-15"},
        {"name": "G-NAF AUG 2026 GDA94", "url": "http://a/aug94.zip", "created": "2026-08-16"},
        {"name": "Readme GDA2020", "url": "http://a/readme.pdf", "created": "2026-09-01"},
    ]
    s = fake_session(lambda m, u, p: fake_response(package(resources)))
    assert latest_gnaf_zip_url(s) == "http://a/aug.zip"
    assert s.calls[0][2] == {"id": GNAF_PACKAGE_ID}


def test_gda2020_in_url_counts(fake_session, fake_response):
    resources = [{"name": "G-NAF", "url": "http://a/g-naf_gda2020.zip", "last_modified": "2026-01-01"}]
    assert latest_gnaf_zip_url(fake_session(lambda m, u, p: fake_response(package(resources)))).endswith(".zip")


def test_raises_when_none_found(fake_session, fake_response):
    with pytest.raises(RuntimeError, match="No GDA2020"):
        latest_gnaf_zip_url(fake_session(lambda m, u, p: fake_response(package([]))))
