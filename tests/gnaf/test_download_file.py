import pytest
import requests

from cadastre_gnaf.gnaf import download_file


def test_streams_to_destination(tmp_path, fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response(chunks=[b"abc", b"def"], headers={"Content-Length": "6"}))
    dest = download_file(s, "http://x/g.zip", tmp_path / "g.zip")
    assert dest.read_bytes() == b"abcdef"
    assert not (tmp_path / "g.part").exists()


def test_skips_complete_existing_file(tmp_path, fake_session, fake_response):
    (tmp_path / "g.zip").write_bytes(b"123456")
    s = fake_session(lambda m, u, p: fake_response(chunks=[b"xxxxxx"], headers={"Content-Length": "6"}))
    download_file(s, "http://x/g.zip", tmp_path / "g.zip")
    assert (tmp_path / "g.zip").read_bytes() == b"123456"


def test_replaces_partial_existing_file(tmp_path, fake_session, fake_response):
    (tmp_path / "g.zip").write_bytes(b"12")
    s = fake_session(lambda m, u, p: fake_response(chunks=[b"abcdef"], headers={"Content-Length": "6"}))
    download_file(s, "http://x/g.zip", tmp_path / "g.zip")
    assert (tmp_path / "g.zip").read_bytes() == b"abcdef"


def test_http_error_raises(tmp_path, fake_session, fake_response):
    s = fake_session(lambda m, u, p: fake_response(status_code=404))
    with pytest.raises(requests.HTTPError):
        download_file(s, "http://x/g.zip", tmp_path / "g.zip")
