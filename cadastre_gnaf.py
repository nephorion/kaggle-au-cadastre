#!/usr/bin/env python3
"""
Australian state cadastres -> per-state flat CSV, keyed to G-NAF.

Downloads each state's land-parcel layer from its public ArcGIS REST service and writes
one CSV per state with source attributes, a point inside each parcel, WKT geometry
(EPSG:4326) and `gnaf_legal_parcel_id` matched against G-NAF's LEGAL_PARCEL_ID. It also
writes an address -> parcel link table per state. Downloads resume if interrupted.

Requirements: Python 3.9+, pandas, numpy, requests; geopandas + shapely for the WA
spatial join and for --local files.

Examples:
  python cadastre_gnaf.py                          # everything, all open states
  python cadastre_gnaf.py --states NSW VIC --step download
  python cadastre_gnaf.py --step gnaf              # G-NAF matching only (after downloading)
  python cadastre_gnaf.py --compress --workers 8 --out D:/cadastre
  python cadastre_gnaf.py --local SA=/data/sa/Parcel_Cadastre.shp --states SA

Sources: NSW Spatial Services, Vicmap (DTP), QSCF (Qld), theLIST (Tas), ACTmapi,
Landgate SLIP public (WA, personal-use terms). SA and NT cadastres are not open data:
supply your own copy with --local. G-NAF: Geoscape via data.gov.au (CC BY 4.0).
"""

import os, re, io, csv, json, math, time, zipfile, shutil, datetime as dt
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

csv.field_size_limit(2**31 - 1)
print("pandas", pd.__version__, "| requests", requests.__version__)

# ============================== CONFIG (command line) ==============================
import argparse
_ap = argparse.ArgumentParser(description="Australian cadastres -> per-state CSV keyed to G-NAF",
                              formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("--states", nargs="+", default=["NSW", "VIC", "QLD", "TAS", "ACT", "WA", "SA", "NT"],
                 help="states to build (default: all; SA/NT need --local)")
_ap.add_argument("--step", choices=["all", "download", "gnaf"], default="all",
                 help="download parcels, G-NAF matching, or both (default)")
_ap.add_argument("--out", default="./cadastre_out", help="output folder for the CSVs")
_ap.add_argument("--work", default="./cadastre_work", help="scratch folder (G-NAF zip, ~1.5 GB)")
_ap.add_argument("--compress", action="store_true", help="write .csv.gz instead of .csv")
_ap.add_argument("--no-wkt", action="store_true", help="omit the WKT geometry column (much smaller)")
_ap.add_argument("--decimals", type=int, default=6, help="coordinate decimals in WKT (default 6, ~0.1 m)")
_ap.add_argument("--workers", type=int, default=4, help="parallel requests per state (default 4)")
_ap.add_argument("--page-size", type=int, default=None, help="features per request (default: server max, capped at 2000)")
_ap.add_argument("--force", action="store_true", help="re-download states already marked done")
_ap.add_argument("--gnaf-dir", default=None, help="folder with an extracted G-NAF release (skips the download)")
_ap.add_argument("--gnaf-zip-url", default=None, help="specific G-NAF zip URL (default: latest GDA2020 release)")
_ap.add_argument("--spatial-join", nargs="*", default=["WA"],
                 help="states that also get a point-in-polygon address join (default: WA)")
_ap.add_argument("--local", nargs="*", default=[], metavar="STATE=PATH",
                 help="licensed/purchased data to use instead of a web service, e.g. SA=/data/sa.shp")
ARGS = _ap.parse_args()

STATES = [s.upper() for s in ARGS.states]
OUT_DIR, WORK_DIR = Path(ARGS.out), Path(ARGS.work)
COMPRESS, INCLUDE_WKT, GEOM_DECIMALS = ARGS.compress, not ARGS.no_wkt, ARGS.decimals
MAX_WORKERS, PAGE_SIZE, FORCE_REDOWNLOAD = ARGS.workers, ARGS.page_size, ARGS.force
DO_GNAF = ARGS.step in ("all", "gnaf")
GNAF_DIR, GNAF_ZIP_URL = ARGS.gnaf_dir, ARGS.gnaf_zip_url
GNAF_PACKAGE_ID = "19432f89-dc3a-4ef3-b943-5326ef1dbecc"   # data.gov.au "Geoscape G-NAF"
SPATIAL_JOIN_STATES = [s.upper() for s in ARGS.spatial_join]
LOCAL_SOURCES = {kv.split("=", 1)[0].upper(): kv.split("=", 1)[1] for kv in ARGS.local}

OUT_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)
CSV_EXT = ".csv.gz" if COMPRESS else ".csv"
print("output ->", OUT_DIR.resolve(), "| scratch ->", WORK_DIR.resolve())

# ===================== G-NAF LEGAL_PARCEL_ID key builders =====================
# Each state returns several candidate keys; the G-NAF step measures which ones
# actually match and uses the first matching one per parcel.

def _val(attrs, *names):
    """Case-insensitive attribute lookup -> clean string ('' if missing)."""
    for n in names:
        for k in (n, n.lower(), n.upper()):
            if k in attrs and attrs[k] is not None:
                v = attrs[k]
                if isinstance(v, float):
                    if math.isnan(v):
                        return ""
                    if v.is_integer():
                        v = int(v)
                s = str(v).strip()
                if s.lower() in ("", "none", "null", "nan"):
                    return ""
                return s
    return ""

def norm_key(s):
    """Normalise a parcel key for comparison: upper-case, no whitespace."""
    if s is None:
        return None
    s = re.sub(r"\s+", "", str(s)).upper()
    return s or None

def _join(*parts, required=None):
    """Join parts with '/'. `required` = indexes that must be non-empty."""
    required = range(len(parts)) if required is None else required
    if any(not parts[i] for i in required):
        return None
    return norm_key("/".join(parts))

def _strip0(s):
    return s.lstrip("0") or ("0" if s else "")

def keys_nsw(a):
    lot, sec = _val(a, "lotnumber"), _val(a, "sectionnumber")
    num, label = _val(a, "plannumber"), _val(a, "planlabel")
    doc = _join(lot, sec, num) if sec else _join(lot, num)       # documented: 13/31993, 11/C/3625
    return {
        "key_lot_sec_plannum": doc,
        "key_lotidstring": norm_key(_val(a, "lotidstring")) ,     # e.g. 1//DP12345
        "key_lot_sec_label": _join(lot, sec, label, required=[0, 2]),
        "key_lot_label": _join(lot, label),
    }

def keys_vic(a):
    return {"key_spi": norm_key(_val(a, "parcel_spi"))}           # e.g. 1TP201500

def keys_qld(a):
    lot, plan = _val(a, "lot"), _val(a, "plan")
    return {
        "key_lot_plan": _join(lot, plan),                          # e.g. 66/RP139841
        "key_lotplan": norm_key(_val(a, "lotplan")),               # e.g. 66RP139841
    }

def keys_tas(a):
    vol, fol = _val(a, "VOLUME"), _val(a, "FOLIO")
    return {
        "key_vol_folio": _join(_strip0(vol), _strip0(fol)),        # e.g. 158882/1
        "key_vol_folio_raw": _join(vol, fol),
    }

def keys_act(a):
    dist, div = _val(a, "DISTRICT_SHORT"), _val(a, "DIVISION_SHORT")
    sec, blk = _val(a, "SECTION_NUMBER"), _val(a, "BLOCK_NUMBER")
    return {
        "key_dist_div_sec_blk": _join(dist, div, sec, blk, required=[0, 3]),  # CANB/BRAD/18/41
        "key_dist_blk": _join(dist, blk),                                     # JERV/927 style
    }

def keys_wa(a):
    # Only usable if you point WA at a SLIP subscription layer that has these fields.
    pi, lot = _val(a, "pi_parcel", "piparcel"), _val(a, "lot_number", "lotnumber")
    return {"key_piparcel_lot": _join(pi, lot)}                     # e.g. S030337/1

def keys_sa(a):
    pt, plan = _val(a, "PLAN_T"), _val(a, "PLAN")
    prt, par = _val(a, "PARCEL_T"), _val(a, "PARCEL")
    return {
        "key_plant_plan_parcelt_parcel": _join(pt, plan, prt, par),  # D/10001/A/14
        "key_dcdbid": norm_key(_val(a, "DCDBID")),
    }

def keys_nt(a):
    loc, par, lto = _val(a, "PAR_LOC"), _val(a, "PAR_PAR"), _val(a, "PAR_LTO")
    return {
        "key_loc_par_lto": _join(loc, _strip0(par), lto, required=[0, 1]),  # 550/3252/
        "key_loc_lto_par": _join(loc, lto, _strip0(par), required=[0, 2]),
    }

# quick self-check
assert keys_nsw({"lotnumber": 13, "sectionnumber": None, "plannumber": 31993, "planlabel": "DP31993"})["key_lot_sec_plannum"] == "13/31993"
assert keys_nsw({"lotnumber": "11", "sectionnumber": "C", "plannumber": 3625})["key_lot_sec_plannum"] == "11/C/3625"
assert keys_qld({"lot": "66", "plan": "RP139841"})["key_lot_plan"] == "66/RP139841"
assert keys_tas({"VOLUME": "158882", "FOLIO": 1})["key_vol_folio"] == "158882/1"
assert keys_act({"DISTRICT_SHORT": "CANB", "DIVISION_SHORT": "BRAD", "SECTION_NUMBER": 18, "BLOCK_NUMBER": 41})["key_dist_div_sec_blk"] == "CANB/BRAD/18/41"
assert keys_sa({"PLAN_T": "D", "PLAN": "10001", "PARCEL_T": "A", "PARCEL": "14"})["key_plant_plan_parcelt_parcel"] == "D/10001/A/14"
print("key builders OK")

# =============================== SOURCES ===============================
SOURCES = {
    "NSW": dict(
        url="https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer/9",
        keys=keys_nsw, licence="CC BY, (c) NSW Spatial Services (DCS)"),
    "VIC": dict(
        url="https://services-ap1.arcgis.com/P744lA0wf4LlBZ84/ArcGIS/rest/services/Vicmap_Parcel/FeatureServer/0",
        keys=keys_vic, licence="CC BY 4.0, (c) State of Victoria (Vicmap Property)"),
    "QLD": dict(
        url="https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/QSCF_LandParcelPropertyFramework/FeatureServer/120",
        keys=keys_qld, licence="CC BY 4.0, (c) State of Queensland"),
    "TAS": dict(
        url="https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreParcels/MapServer/0",
        keys=keys_tas, licence="CC BY 3.0 AU, (c) State of Tasmania (theLIST); see LIST Web Services T&Cs"),
    "ACT": dict(
        url="https://services1.arcgis.com/E5n4f1VY84i0xSjy/ArcGIS/rest/services/ACTGOV_BLOCKS/FeatureServer/0",
        keys=keys_act, licence="(c) Australian Capital Territory (ACTmapi)"),
    "WA": dict(
        # LGATE-001 "Cadastre (No Attributes)": geometry only, public under personal-use terms.
        # With a SLIP subscription, swap in a fully attributed layer (and set token below).
        url="https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Property_and_Planning/MapServer/2",
        keys=keys_wa, licence="Landgate SLIP public services, personal-use licence"),
    "SA": dict(url=None, keys=keys_sa, licence="Purchased from Land Services SA (not open data)"),
    "NT": dict(url=None, keys=keys_nt, licence="NT Government (NTLIS), not open data"),
}
ARCGIS_TOKENS = {}   # e.g. {"WA": "<SLIP token>"} if you use a subscription service

# ===================== Esri JSON geometry -> WKT (pure Python) =====================
def _local(ring):
    """Shift a ring to its first vertex: avoids float cancellation at lon ~150."""
    x0, y0 = ring[0]
    return [(x - x0, y - y0) for x, y in ring], x0, y0

def _signed_area(ring):
    r, _, _ = _local(ring)
    s = 0.0
    for (x1, y1), (x2, y2) in zip(r, r[1:]):
        s += x1 * y2 - x2 * y1
    return s / 2.0

def _point_in_ring(x, y, ring):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                inside = not inside
    return inside

def _ring_centroid(ring, area):
    if area == 0:
        xs, ys = zip(*ring)
        return sum(xs) / len(xs), sum(ys) / len(ys)
    r, x0, y0 = _local(ring)
    cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(r, r[1:]):
        f = x1 * y2 - x2 * y1
        cx += (x1 + x2) * f
        cy += (y1 + y2) * f
    return x0 + cx / (6 * area), y0 + cy / (6 * area)

def _scanline_point(shell, holes):
    """Point inside polygon: midpoint of the widest interior span on the line through the bbox middle."""
    ys = [p[1] for p in shell]
    y = (min(ys) + max(ys)) / 2.0
    xs = []
    for ring in [shell] + holes:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            if (y1 > y) != (y2 > y):
                xs.append((x2 - x1) * (y - y1) / (y2 - y1) + x1)
    xs.sort()
    best = None
    for a, b in zip(xs[0::2], xs[1::2]):
        if best is None or (b - a) > (best[1] - best[0]):
            best = (a, b)
    if best is None:
        return shell[0]
    return (best[0] + best[1]) / 2.0, y

def _fmt(v, d):
    s = f"{v:.{d}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s

def _ring_wkt(ring, d):
    return "(" + ",".join(f"{_fmt(x, d)} {_fmt(y, d)}" for x, y in ring) + ")"

def esri_to_wkt(geom, decimals=6):
    """Return (wkt, point_lon, point_lat) for an Esri JSON polygon/point geometry."""
    if not geom:
        return "", None, None
    if "x" in geom and "y" in geom:
        if geom["x"] is None:
            return "", None, None
        return f"POINT ({_fmt(geom['x'], decimals)} {_fmt(geom['y'], decimals)})", geom["x"], geom["y"]
    rings = []
    for r in geom.get("rings") or []:
        r = [(float(p[0]), float(p[1])) for p in r if p is not None and len(p) >= 2]
        if len(r) < 3:
            continue
        if r[0] != r[-1]:
            r.append(r[0])
        if len(r) >= 4:
            rings.append(r)
    if not rings:
        return "", None, None
    areas = [_signed_area(r) for r in rings]
    shells = [i for i, a in enumerate(areas) if a < 0]        # Esri: outer rings are clockwise
    holes = [i for i, a in enumerate(areas) if a >= 0]
    if not shells:                                           # non-standard orientation: treat all as shells
        shells, holes = list(range(len(rings))), []
    polys = {i: [] for i in shells}
    for h in holes:
        hx, hy = rings[h][0]
        owner = next((s for s in shells if _point_in_ring(hx, hy, rings[s])), None)
        if owner is None:                                    # orphan hole -> its own polygon
            polys[h] = []
        else:
            polys[owner].append(h)
    parts = [(s, hs) for s, hs in polys.items()]
    parts_wkt = ["(" + ",".join(_ring_wkt(rings[i], decimals) for i in [s] + hs) + ")" for s, hs in parts]
    wkt = ("POLYGON " + parts_wkt[0]) if len(parts_wkt) == 1 else ("MULTIPOLYGON (" + ",".join(parts_wkt) + ")")
    # representative point: centroid of the largest part if it falls inside, else a scanline point
    s, hs = max(parts, key=lambda p: abs(areas[p[0]]))
    shell, hole_rings = rings[s], [rings[h] for h in hs]
    cx, cy = _ring_centroid(shell, _signed_area(shell))
    if not (_point_in_ring(cx, cy, shell) and not any(_point_in_ring(cx, cy, h) for h in hole_rings)):
        cx, cy = _scanline_point(shell, hole_rings)
    return wkt, round(cx, decimals + 1), round(cy, decimals + 1)

# self-check: square with a hole (Esri orientation: shell clockwise, hole counter-clockwise)
_w, _x, _y = esri_to_wkt({"rings": [[[0,0],[0,10],[10,10],[10,0],[0,0]], [[4,4],[6,4],[6,6],[4,6],[4,4]]]})
assert _w.startswith("POLYGON ((0 0,0 10") and "(4 4,6 4" in _w, _w
assert not (4 < _x < 6 and 4 < _y < 6), (_x, _y)      # point avoids the hole
_w, _x, _y = esri_to_wkt({"rings": [[[151.2001, -33.8], [151.2001, -33.799], [151.2011, -33.799], [151.2011, -33.8], [151.2001, -33.8]]]})
assert abs(_x - 151.2006) < 1e-9 and abs(_y + 33.7995) < 1e-9, (_x, _y)   # centroid exact at real coords
_w, _x, _y = esri_to_wkt({"rings": [[[0,0],[0,1],[1,1],[1,0],[0,0]], [[5,5],[5,6],[6,6],[6,5],[5,5]]]})
assert _w.startswith("MULTIPOLYGON")
print("geometry OK")

# ======================= ArcGIS REST downloader =======================
SESSION = requests.Session()
SESSION.headers["User-Agent"] = "kaggle-au-cadastre-notebook/1.0 (research; polite paging)"

class ArcGISError(RuntimeError):
    pass

def arcgis_get(url, params, retries=6, timeout=180):
    """GET (POST for long queries) with retries; raises on ArcGIS JSON errors after retries."""
    params = {"f": "json", **params}
    last = None
    for attempt in range(retries):
        try:
            long_q = len(str(params)) > 1500
            r = (SESSION.post(url, data=params, timeout=timeout) if long_q
                 else SESSION.get(url, params=params, timeout=timeout))
            if r.status_code in (429, 500, 502, 503, 504):
                raise ArcGISError(f"HTTP {r.status_code}")
            r.raise_for_status()
            js = r.json()
            if isinstance(js, dict) and "error" in js:
                raise ArcGISError(js["error"])
            return js
        except (requests.RequestException, ValueError, ArcGISError) as e:
            last = e
            time.sleep(min(60, 2 ** attempt + np.random.rand()))
    raise ArcGISError(f"{url} failed after {retries} tries: {last}")

def layer_info(url, token=None):
    p = {"token": token} if token else {}
    info = arcgis_get(url, p)
    oid = info.get("objectIdField") or next(
        (f["name"] for f in info.get("fields", []) if f.get("type") == "esriFieldTypeOID"), None)
    if not oid:
        raise ArcGISError(f"No ObjectID field found for {url}")
    return info, oid

def oid_bounds(url, oid, where="1=1", token=None, at_least=None):
    """Min/max ObjectID (optionally min OID >= at_least). Uses statistics, falls back to ID list."""
    w = where if at_least is None else f"({where}) AND {oid} >= {int(at_least)}"
    p = {"where": w, "returnGeometry": "false",
         "outStatistics": json.dumps([
             {"statisticType": "min", "onStatisticField": oid, "outStatisticFieldName": "mn"},
             {"statisticType": "max", "onStatisticField": oid, "outStatisticFieldName": "mx"}])}
    if token: p["token"] = token
    try:
        js = arcgis_get(url + "/query", p, retries=3)
        a = {k.lower(): v for k, v in js["features"][0]["attributes"].items()}
        return a.get("mn"), a.get("mx")
    except Exception:
        p = {"where": w, "returnIdsOnly": "true"}
        if token: p["token"] = token
        ids = arcgis_get(url + "/query", p).get("objectIds") or []
        return (min(ids), max(ids)) if ids else (None, None)

def fetch_range(url, oid, lo, hi, where="1=1", token=None, depth=0):
    """All features with lo <= OID < hi. Splits the range if the server truncates."""
    p = {"where": f"({where}) AND {oid} >= {lo} AND {oid} < {hi}", "outFields": "*",
         "returnGeometry": "true", "outSR": 4326, "geometryPrecision": GEOM_DECIMALS + 1}
    if token: p["token"] = token
    js = arcgis_get(url + "/query", p)
    feats = js.get("features", [])
    if js.get("exceededTransferLimit") and hi - lo > 1 and depth < 20:
        mid = (lo + hi) // 2
        return (fetch_range(url, oid, lo, mid, where, token, depth + 1) +
                fetch_range(url, oid, mid, hi, where, token, depth + 1))
    return feats

# =================== Per-state download -> flat CSV ===================
PROGRESS_DIR = OUT_DIR / "_progress"
PROGRESS_DIR.mkdir(exist_ok=True)

def parcels_path(state):
    return OUT_DIR / f"{state}_parcels{CSV_EXT}"

def _progress(state, data=None):
    p = PROGRESS_DIR / f"{state}.json"
    if data is None:
        return json.loads(p.read_text()) if p.exists() else {}
    p.write_text(json.dumps(data))

def _key_names(spec):
    return list(spec["keys"]({}).keys())

def _rows_from_attrs(state, spec, items, date_fields, oid):
    """items: iterable of (attrs, wkt, lon, lat) -> list of row dicts."""
    rows = []
    for attrs, wkt, lon, lat in items:
        row = {"state": state, "source_oid": attrs.get(oid)}
        row.update(spec["keys"](attrs))
        row["point_lon"], row["point_lat"] = lon, lat
        for k, v in attrs.items():
            if k in date_fields and v not in (None, ""):
                try:
                    v = dt.datetime.fromtimestamp(v / 1000, dt.timezone.utc).date().isoformat()
                except Exception:
                    pass
            row[k if k not in BASE_COLS else f"src_{k}"] = v
        if INCLUDE_WKT:
            row["wkt"] = wkt
        rows.append(row)
    return rows

BASE_COLS = {"state", "source_oid", "point_lon", "point_lat", "wkt",
             "gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count"}

def _columns(state, spec, attr_names):
    cols = ["state", "source_oid"] + _key_names(spec) + ["point_lon", "point_lat"]
    cols += [c if c not in BASE_COLS else f"src_{c}" for c in attr_names]
    return cols + (["wkt"] if INCLUDE_WKT else [])

def _append(path, df, cols, first):
    df.reindex(columns=cols).to_csv(path, mode="w" if first else "a", header=first, index=False,
                                    compression="gzip" if COMPRESS else None)

def download_arcgis_state(state):
    spec, token = SOURCES[state], ARCGIS_TOKENS.get(state)
    url, where = spec["url"], spec.get("where", "1=1")
    out = parcels_path(state)
    prog = _progress(state)
    if prog.get("done") and out.exists() and not FORCE_REDOWNLOAD:
        print(f"[{state}] already downloaded ({prog.get('rows'):,} rows) -> {out.name}")
        return
    if FORCE_REDOWNLOAD or not out.exists():
        prog = {}

    info, oid = layer_info(url, token)
    fields = [f for f in info.get("fields", []) if f.get("type") != "esriFieldTypeGeometry"]
    date_fields = {f["name"] for f in fields if f.get("type") == "esriFieldTypeDate"}
    cols = _columns(state, spec, [f["name"] for f in fields])
    step = int(PAGE_SIZE or min(int(info.get("maxRecordCount") or 1000), 2000))
    cnt = arcgis_get(url + "/query", {"where": where, "returnCountOnly": "true",
                                      **({"token": token} if token else {})}).get("count")
    mn, mx = oid_bounds(url, oid, where, token)
    print(f"[{state}] {info.get('name')} | {cnt:,} features | OID {mn}..{mx} | page {step}")
    if mn is None:
        return

    a, rows_total, first = prog.get("next", mn), prog.get("rows", 0), "next" not in prog
    t0 = time.time()
    with ThreadPoolExecutor(MAX_WORKERS) as pool:
        while a <= mx:
            ranges = [(a + i * step, a + (i + 1) * step) for i in range(MAX_WORKERS * 2)]
            batches = list(pool.map(lambda r: fetch_range(url, oid, r[0], r[1], where, token), ranges))
            feats = [f for b in batches for f in b]
            items = []
            for f in feats:
                wkt, lon, lat = esri_to_wkt(f.get("geometry"), GEOM_DECIMALS)
                items.append((f.get("attributes", {}), wkt, lon, lat))
            if items:
                _append(out, pd.DataFrame(_rows_from_attrs(state, spec, items, date_fields, oid)), cols, first)
                first = False
                rows_total += len(items)
            a = ranges[-1][1]
            if not feats:                                   # gap in OIDs: jump to the next one
                nxt, _ = oid_bounds(url, oid, where, token, at_least=a)
                if nxt is None:
                    break
                a = max(a, int(nxt))
            _progress(state, {"next": a, "rows": rows_total, "expected": cnt})
            rate = rows_total / max(1, time.time() - t0)
            print(f"\r[{state}] {rows_total:,}/{cnt:,} rows  ({rate:,.0f}/s)", end="", flush=True)
    _progress(state, {"next": a, "rows": rows_total, "expected": cnt, "done": True,
                      "columns": cols, "finished": dt.datetime.now().isoformat()})
    print(f"\n[{state}] done: {rows_total:,} rows -> {out}")

def load_local_state(state, path):
    """Licensed/purchased data (SA, NT, or a WA subscription extract) read with geopandas."""
    import geopandas as gpd
    spec = SOURCES[state]
    gdf = gpd.read_file(path)
    gdf = gdf.set_crs(4326) if gdf.crs is None else gdf.to_crs(4326)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
    attr_names = [c for c in gdf.columns if c != gdf.geometry.name]
    gdf["__oid"] = np.arange(1, len(gdf) + 1)
    cols = _columns(state, spec, attr_names)
    out, first = parcels_path(state), True
    for start in range(0, len(gdf), 100_000):
        part = gdf.iloc[start:start + 100_000]
        pts = part.geometry.representative_point()
        wkts = part.geometry.to_wkt(rounding_precision=GEOM_DECIMALS) if INCLUDE_WKT else [""] * len(part)
        recs = part[attr_names + ["__oid"]].to_dict("records")
        items = []
        for rec, w, p in zip(recs, wkts, pts):
            rec = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in rec.items()}
            items.append((rec, w, round(p.x, GEOM_DECIMALS + 1), round(p.y, GEOM_DECIMALS + 1)))
        _append(out, pd.DataFrame(_rows_from_attrs(state, spec, items, set(), "__oid")), cols, first)
        first = False
    _progress(state, {"rows": len(gdf), "expected": len(gdf), "done": True, "columns": cols, "source": str(path)})
    print(f"[{state}] {len(gdf):,} rows from {path} -> {out}")

def run_downloads():
    # ========================= RUN: download every state =========================
    failures = {}
    for st in STATES:
        try:
            if st in LOCAL_SOURCES:
                load_local_state(st, LOCAL_SOURCES[st])
            elif SOURCES[st]["url"]:
                download_arcgis_state(st)
            else:
                print(f"[{st}] skipped: no open service. Use --local {st}=/path/to/file (see --help).")
        except Exception as e:                       # keep going; re-run this cell to resume
            failures[st] = repr(e)
            print(f"\n[{st}] FAILED: {e!r}  (re-run this cell to resume)")
    print("failures:", failures or "none")
    return failures

# ============================ G-NAF ============================
def latest_gnaf_zip_url():
    api = "https://data.gov.au/data/api/3/action/package_show"
    res = SESSION.get(api, params={"id": GNAF_PACKAGE_ID}, timeout=60).json()["result"]["resources"]
    cands = [r for r in res if str(r.get("url", "")).lower().endswith(".zip")
             and "gda2020" in (str(r.get("name", "")) + str(r.get("url", ""))).lower()]
    if not cands:
        raise RuntimeError("No GDA2020 G-NAF zip found on data.gov.au; set GNAF_ZIP_URL manually.")
    cands.sort(key=lambda r: r.get("created") or r.get("last_modified") or "", reverse=True)
    print("G-NAF release:", cands[0].get("name"))
    return cands[0]["url"]

def download(url, dest, chunk=8 << 20):
    dest = Path(dest)
    with SESSION.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        if dest.exists() and total and dest.stat().st_size == total:
            print("already downloaded:", dest)
            return dest
        done, tmp = 0, dest.with_suffix(".part")
        with open(tmp, "wb") as fh:
            for b in r.iter_content(chunk):
                fh.write(b)
                done += len(b)
                print(f"\r  {done/1e9:.2f} / {total/1e9:.2f} GB", end="", flush=True)
        tmp.rename(dest)
    print()
    return dest

class Gnaf:
    """Reads per-state PSV tables from the G-NAF zip (or an extracted folder) without unpacking it all."""
    def __init__(self):
        if GNAF_DIR:
            self.zip, self.root = None, Path(GNAF_DIR)
        else:
            z = WORK_DIR / "gnaf.zip"
            download(GNAF_ZIP_URL or latest_gnaf_zip_url(), z)
            self.zip, self.root = zipfile.ZipFile(z), None

    def _open(self, state, table):
        pat = re.compile(rf"(^|/)Standard/{state}_{table}_psv\.psv$", re.I)
        if self.zip:
            name = next((n for n in self.zip.namelist() if pat.search(n)), None)
            if not name:
                raise FileNotFoundError(f"{state}_{table} not in G-NAF zip")
            return self.zip.open(name)
        hit = next((p for p in self.root.rglob(f"{state}_{table}_psv.psv")), None)
        if not hit:
            raise FileNotFoundError(f"{state}_{table} not under {self.root}")
        return open(hit, "rb")

    def table(self, state, table, usecols):
        with self._open(state, table) as fh:
            df = pd.read_csv(fh, sep="|", dtype=str, usecols=lambda c: c in usecols, keep_default_na=False)
        if "DATE_RETIRED" in df:
            df = df[df["DATE_RETIRED"] == ""].drop(columns="DATE_RETIRED")
        return df

    def parcels(self, state):
        df = self.table(state, "ADDRESS_DETAIL", {"ADDRESS_DETAIL_PID", "LEGAL_PARCEL_ID", "DATE_RETIRED"})
        df["key"] = df["LEGAL_PARCEL_ID"].map(norm_key)
        return df

    def points(self, state):
        df = self.table(state, "ADDRESS_DEFAULT_GEOCODE", {"ADDRESS_DETAIL_PID", "LONGITUDE", "LATITUDE", "DATE_RETIRED"})
        df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
        df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
        return df.dropna(subset=["LONGITUDE", "LATITUDE"])

GNAF = None

# ============ Pick the G-NAF key, link addresses, finalise each CSV ============
def links_path(state):
    return OUT_DIR / f"{state}_gnaf_address_parcel_links{CSV_EXT}"

def spatial_links(state, points, chunk=500_000):
    """Point-in-polygon join of G-NAF default geocodes to parcel polygons (needs geopandas)."""
    import geopandas as gpd
    from shapely import from_wkt
    parts = []
    for c in pd.read_csv(parcels_path(state), usecols=["source_oid", "wkt"], dtype={"wkt": str}, chunksize=500_000):
        c = c[c["wkt"].fillna("") != ""]
        parts.append(gpd.GeoDataFrame(c[["source_oid"]], geometry=from_wkt(c["wkt"].values), crs=4326))
    from shapely import make_valid
    polys = pd.concat(parts, ignore_index=True)
    polys = polys[polys.geometry.notna()].copy()
    bad = ~polys.is_valid
    polys.loc[bad, "geometry"] = make_valid(polys.loc[bad, "geometry"].values)
    out = []
    for i in range(0, len(points), chunk):
        p = points.iloc[i:i + chunk]
        g = gpd.GeoDataFrame(p[["ADDRESS_DETAIL_PID"]],
                             geometry=gpd.points_from_xy(p["LONGITUDE"], p["LATITUDE"]), crs=4326)
        j = gpd.sjoin(g, polys, predicate="within", how="inner")
        out.append(pd.DataFrame({"address_detail_pid": j["ADDRESS_DETAIL_PID"].values,
                                 "source_oid": j["source_oid"].values}))
        print(f"\r  [{state}] spatial join {min(i + chunk, len(points)):,}/{len(points):,} points", end="", flush=True)
    print()
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["address_detail_pid", "source_oid"])

def finalise_state(state):
    path = parcels_path(state)
    if not path.exists():
        return None
    spec = SOURCES[state]
    knames = _key_names(spec)
    kd = pd.read_csv(path, usecols=["source_oid"] + knames, dtype=str, keep_default_na=False)
    kd = kd.drop_duplicates("source_oid").set_index("source_oid")
    kd = kd.replace("", np.nan)
    summ = {"state": state, "parcels": len(kd)}

    if GNAF is not None:
        g = GNAF.parcels(state)
        gset = set(g["key"].dropna())
        stats = []
        for k in knames:
            v = kd[k].dropna()
            m = v.isin(gset)
            stats.append((k, int(m.sum()), len(v)))
        stats.sort(key=lambda s: -s[1])
        ranked = [s[0] for s in stats]
        summ["key_match"] = {k: f"{n:,}/{t:,}" for k, n, t in stats}
        print(f"[{state}] parcels matching G-NAF LEGAL_PARCEL_ID by candidate:", summ["key_match"])
        chosen = pd.Series(np.nan, index=kd.index, dtype=object)
        matched = pd.Series(False, index=kd.index)
        for k in ranked:                                   # first candidate that matches
            hit = kd[k].isin(gset) & ~matched
            chosen[hit], matched[hit] = kd.loc[hit, k], True
        for k in ranked:                                   # otherwise best-ranked non-empty value
            fill = chosen.isna() & kd[k].notna()
            chosen[fill] = kd.loc[fill, k]
        # address -> parcel links via the key
        pk = pd.DataFrame({"source_oid": chosen[matched].index, "key": chosen[matched].values})
        links = g.merge(pk, on="key", how="inner")[["ADDRESS_DETAIL_PID", "LEGAL_PARCEL_ID", "source_oid"]]
        links.columns = ["address_detail_pid", "legal_parcel_id", "source_oid"]
        links["method"] = "legal_parcel_id"
        if state in SPATIAL_JOIN_STATES and INCLUDE_WKT:
            todo = set(g["ADDRESS_DETAIL_PID"]) - set(links["address_detail_pid"])
            pts = GNAF.points(state)
            pts = pts[pts["ADDRESS_DETAIL_PID"].isin(todo)]
            sj = spatial_links(state, pts)
            sj = sj.merge(g[["ADDRESS_DETAIL_PID", "LEGAL_PARCEL_ID"]].rename(
                columns={"ADDRESS_DETAIL_PID": "address_detail_pid", "LEGAL_PARCEL_ID": "legal_parcel_id"}),
                on="address_detail_pid", how="left")
            sj["method"] = "spatial_within"
            links = pd.concat([links, sj], ignore_index=True)
        links["source_oid"] = links["source_oid"].astype(str)
        links.to_csv(links_path(state), index=False, compression="gzip" if COMPRESS else None)
        counts = links.groupby("source_oid")["address_detail_pid"].nunique()
        summ["gnaf_addresses"] = len(g)
        summ["addresses_linked"] = int(links["address_detail_pid"].nunique())
        summ["address_link_rate"] = round(summ["addresses_linked"] / max(1, len(g)), 4)
        summ["parcels_with_gnaf_key_match"] = int(matched.sum())
    else:
        chosen = kd.bfill(axis=1).iloc[:, 0] if knames else pd.Series(np.nan, index=kd.index)
        matched, counts = pd.Series(False, index=kd.index), pd.Series(dtype=int)

    # rewrite the parcels CSV with the three G-NAF columns, de-duplicated by source_oid
    tmp = path.with_name(path.name + ".tmp")
    seen, first = set(), True
    for c in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=200_000):
        c = c.drop(columns=[x for x in ("gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count") if x in c])
        c = c[~c["source_oid"].isin(seen)].drop_duplicates("source_oid")
        seen.update(c["source_oid"])
        pos = 2 + len(knames)
        c.insert(pos, "gnaf_legal_parcel_id", c["source_oid"].map(chosen).fillna(""))
        c.insert(pos + 1, "gnaf_key_matched", c["source_oid"].map(matched).fillna(False))
        c.insert(pos + 2, "gnaf_address_count", c["source_oid"].map(counts).fillna(0).astype(int))
        c.to_csv(tmp, mode="w" if first else "a", header=first, index=False,
                 compression="gzip" if COMPRESS else None)
        first = False
    tmp.replace(path)
    print(f"[{state}] finalised {path.name}: {summ}")
    return summ


def run_gnaf():
    global GNAF
    GNAF = Gnaf()
    summaries = []
    for st in STATES:
        try:
            s = finalise_state(st)
            if s: summaries.append(s)
        except Exception as e:
            print(f"[{st}] finalise FAILED: {e!r}")
    return summaries

def write_summary(summaries):
    # ===================== Summary, attribution, file list =====================
    rows = []
    for st in STATES:
        p = _progress(st)
        s = next((x for x in summaries if x["state"] == st), {})
        rows.append({
            "state": st,
            "source": SOURCES[st]["url"] or LOCAL_SOURCES.get(st, "not available (licensed)"),
            "features_expected": p.get("expected"),
            "parcels_written": s.get("parcels"),
            "parcels_matching_gnaf_key": s.get("parcels_with_gnaf_key_match"),
            "gnaf_addresses": s.get("gnaf_addresses"),
            "address_link_rate": s.get("address_link_rate"),
            "key_match_by_candidate": json.dumps(s.get("key_match")) if s.get("key_match") else None,
            "licence": SOURCES[st]["licence"],
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT_DIR / "summary.csv", index=False)

    (OUT_DIR / "ATTRIBUTION.md").write_text(
        "# Data sources and licences\n\n"
        + "\n".join(f"- **{r['state']}**: {r['licence']}. Source: {r['source']}" for r in rows)
        + "\n- **G-NAF**: Geoscape Australia, Geocoded National Address File, via data.gov.au "
          "(CC BY 4.0, subject to the Open G-NAF use restriction).\n\n"
          "Cadastral polygons are graphical representations only, not legal boundaries. "
          "Built " + dt.datetime.now().isoformat(timespec="minutes") + ".\n")

    print(summary.to_string(index=False))
    for f in sorted(OUT_DIR.glob("*")):
        if f.is_file():
            print(f"{f.stat().st_size/1e6:10.1f} MB  {f.name}")

def main():
    t0 = time.time()
    failures, summaries = {}, []
    if ARGS.step in ("all", "download"):
        failures = run_downloads()
    if DO_GNAF:
        summaries = run_gnaf()
    write_summary(summaries)
    print(f"finished in {(time.time() - t0) / 3600:.2f} h" + (f"; failed: {list(failures)}" if failures else ""))


if __name__ == "__main__":
    main()
