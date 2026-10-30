import importlib
import shutil
from dataclasses import replace

from cadastre_gnaf.gnaf import open_gnaf

mod = importlib.import_module("cadastre_gnaf.gnaf.open_gnaf")


def test_uses_extracted_folder(config, gnaf_dir):
    src = open_gnaf(replace(config, gnaf_dir=gnaf_dir), session=None)
    assert src.root == gnaf_dir and src.zip is None


def test_downloads_configured_zip(config, gnaf_zip_path, monkeypatch):
    seen = {}

    def fake_download(session, url, dest):
        seen["url"] = url
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(gnaf_zip_path, dest)
        return dest

    monkeypatch.setattr(mod, "download_file", fake_download)
    src = open_gnaf(replace(config, gnaf_zip_url="http://x/g.zip"), session=None)
    assert seen["url"] == "http://x/g.zip"
    assert any(n.endswith("ACT_ADDRESS_DETAIL_psv.psv") for n in src.zip.namelist())
    src.zip.close()


def test_falls_back_to_latest_release(config, gnaf_zip_path, monkeypatch):
    seen = {}

    def fake_download(session, url, dest):
        seen["url"] = url
        shutil.copy(gnaf_zip_path, dest)

    monkeypatch.setattr(mod, "latest_gnaf_zip_url", lambda session: "http://latest.zip")
    monkeypatch.setattr(mod, "download_file", fake_download)
    config.work_dir.mkdir(parents=True)
    open_gnaf(config, session=None).zip.close()
    assert seen["url"] == "http://latest.zip"
