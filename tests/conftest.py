"""Shared fixtures: a fake HTTP session, a fake ArcGIS layer and a tiny G-NAF release."""

import re
import zipfile

import pytest
import requests

from cadastre_gnaf.config import Config


class FakeResponse:
    def __init__(self, json_data=None, status_code=200, chunks=(), headers=None):
        self._json, self.status_code = json_data, status_code
        self._chunks, self.headers = list(chunks), headers or {}

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size):
        yield from self._chunks

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeSession:
    """Routes get/post to `handler(method, url, params)`, which returns a FakeResponse or raises."""

    def __init__(self, handler):
        self.handler, self.calls, self.headers = handler, [], {}

    def _respond(self, method, url, params):
        self.calls.append((method, url, dict(params or {})))
        r = self.handler(method, url, dict(params or {}))
        if isinstance(r, Exception):
            raise r
        return r

    def get(self, url, params=None, **kw):
        return self._respond("GET", url, params)

    def post(self, url, data=None, **kw):
        return self._respond("POST", url, data)


def _arcgis_layer_handler(features, max_records=1000, oid="OBJECTID", fields=None, name="Parcels"):
    """Emulates an ArcGIS FeatureServer layer holding `features` (Esri JSON dicts)."""
    fields = fields or [{"name": oid, "type": "esriFieldTypeOID"},
                        {"name": "BLOCK", "type": "esriFieldTypeString"},
                        {"name": "SHAPE", "type": "esriFieldTypeGeometry"}]

    def oids_in(where):
        lo = re.search(rf"{oid} >= (\d+)", where)
        hi = re.search(rf"{oid} < (\d+)", where)
        return [f for f in features
                if (not lo or f["attributes"][oid] >= int(lo.group(1)))
                and (not hi or f["attributes"][oid] < int(hi.group(1)))]

    def handler(method, url, params):
        if not url.endswith("/query"):
            return FakeResponse({"name": name, "objectIdField": oid, "fields": fields,
                                 "maxRecordCount": max_records})
        hits = oids_in(params.get("where", ""))
        if params.get("returnCountOnly"):
            return FakeResponse({"count": len(hits)})
        if params.get("outStatistics"):
            ids = [f["attributes"][oid] for f in hits]
            return FakeResponse({"features": [{"attributes": {"MN": min(ids) if ids else None,
                                                              "MX": max(ids) if ids else None}}]})
        if params.get("returnIdsOnly"):
            return FakeResponse({"objectIds": [f["attributes"][oid] for f in hits]})
        return FakeResponse({"features": hits[:max_records], "exceededTransferLimit": len(hits) > max_records})

    return handler


@pytest.fixture
def fake_session():
    """Factory: fake_session(handler) -> FakeSession."""
    return FakeSession


@pytest.fixture
def fake_response():
    return FakeResponse


@pytest.fixture
def arcgis_layer():
    """Factory: arcgis_layer(features, max_records=...) -> FakeSession serving that layer."""
    return lambda features, **kw: FakeSession(_arcgis_layer_handler(features, **kw))


@pytest.fixture
def square_feature():
    """Factory for an Esri polygon feature: a 1x1 square at (x, y), clockwise (Esri outer ring)."""
    def make(oid, x=149.0, y=-35.0, **attrs):
        ring = [[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y], [x, y]]
        return {"attributes": {"OBJECTID": oid, **attrs}, "geometry": {"rings": [ring]}}
    return make


@pytest.fixture
def config(tmp_path):
    return Config(states=("ACT",), out_dir=tmp_path / "out", work_dir=tmp_path / "work", workers=2)


ADDRESS_DETAIL = (
    "ADDRESS_DETAIL_PID|DATE_RETIRED|LEGAL_PARCEL_ID|OTHER\n"
    "GAACT1|| CANB/BRAD/18/41 |x\n"
    "GAACT2||CANB/BRAD/18/41|x\n"
    "GAACT3||CANB/BRAD/18/42|x\n"
    "GAACT4|2020-01-01|CANB/BRAD/18/41|x\n"
    "GAACT5|||x\n"
)
ADDRESS_DEFAULT_GEOCODE = (
    "ADDRESS_DETAIL_PID|DATE_RETIRED|LONGITUDE|LATITUDE\n"
    "GAACT1||149.5|-34.5\n"
    "GAACT2||149.5|-34.5\n"
    "GAACT3||150.5|-34.5\n"
    "GAACT5||149.5|-34.5\n"
    "GAACT6||bad|-34.5\n"
)


@pytest.fixture
def gnaf_zip_path(tmp_path):
    """A G-NAF-shaped zip with ACT ADDRESS_DETAIL and ADDRESS_DEFAULT_GEOCODE tables."""
    path = tmp_path / "gnaf.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("G-NAF/G-NAF AUG 2026/Standard/ACT_ADDRESS_DETAIL_psv.psv", ADDRESS_DETAIL)
        z.writestr("G-NAF/G-NAF AUG 2026/Standard/ACT_ADDRESS_DEFAULT_GEOCODE_psv.psv", ADDRESS_DEFAULT_GEOCODE)
    return path


@pytest.fixture
def gnaf_dir(tmp_path):
    """The same tables as `gnaf_zip_path`, as an extracted folder."""
    root = tmp_path / "gnaf_extracted"
    std = root / "G-NAF" / "Standard"
    std.mkdir(parents=True)
    (std / "ACT_ADDRESS_DETAIL_psv.psv").write_text(ADDRESS_DETAIL)
    (std / "ACT_ADDRESS_DEFAULT_GEOCODE_psv.psv").write_text(ADDRESS_DEFAULT_GEOCODE)
    return root


@pytest.fixture
def gnaf(gnaf_zip_path):
    from cadastre_gnaf.gnaf import GnafSource
    with zipfile.ZipFile(gnaf_zip_path) as z:
        yield GnafSource(zip=z)
