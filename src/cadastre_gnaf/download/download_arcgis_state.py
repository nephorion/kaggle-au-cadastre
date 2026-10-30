import datetime as dt
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from cadastre_gnaf.arcgis import feature_count, fetch_range, layer_info, oid_bounds
from cadastre_gnaf.download.page_ranges import page_ranges
from cadastre_gnaf.download.page_size import page_size
from cadastre_gnaf.keys import key_names
from cadastre_gnaf.storage import append_csv, parcels_path, read_progress, write_progress
from cadastre_gnaf.tabular import features_to_items, output_columns, rows_from_items


def download_arcgis_state(config, session, state, source):
    """Page through a state's ArcGIS layer by ObjectID into its parcels CSV. Resumable."""
    token = config.arcgis_tokens.get(state)
    url, where = source.url, source.where
    out = parcels_path(config, state)
    prog = read_progress(config, state)
    if prog.get("done") and out.exists() and not config.force:
        print(f"[{state}] already downloaded ({prog.get('rows', 0):,} rows) -> {out.name}")
        return
    if config.force or not out.exists():
        prog = {}

    info, oid = layer_info(session, url, token)
    fields = [f for f in info.get("fields", []) if f.get("type") != "esriFieldTypeGeometry"]
    date_fields = {f["name"] for f in fields if f.get("type") == "esriFieldTypeDate"}
    cols = output_columns(key_names(source.keys), [f["name"] for f in fields], config.include_wkt)
    step = page_size(config.page_size, info)
    cnt = feature_count(session, url, where, token)
    mn, mx = oid_bounds(session, url, oid, where, token)
    print(f"[{state}] {info.get('name')} | {cnt:,} features | OID {mn}..{mx} | page {step}")
    if mn is None:
        return

    a, rows_total, first = prog.get("next", mn), prog.get("rows", 0), "next" not in prog
    t0 = time.time()
    with ThreadPoolExecutor(config.workers) as pool:
        while a <= mx:
            ranges = page_ranges(a, step, config.workers * 2)
            batches = list(pool.map(
                lambda r: fetch_range(session, url, oid, r[0], r[1], where, token, config.decimals), ranges))
            feats = [f for b in batches for f in b]
            items = features_to_items(feats, config.decimals)
            if items:
                rows = rows_from_items(state, source.keys, items, date_fields, oid, config.include_wkt)
                append_csv(out, pd.DataFrame(rows), cols, first, config.compression)
                first = False
                rows_total += len(items)
            a = ranges[-1][1]
            if not feats:                                   # gap in OIDs: jump to the next one
                nxt, _ = oid_bounds(session, url, oid, where, token, at_least=a)
                if nxt is None:
                    break
                a = max(a, int(nxt))
            write_progress(config, state, {"next": a, "rows": rows_total, "expected": cnt})
            rate = rows_total / max(1, time.time() - t0)
            print(f"\r[{state}] {rows_total:,}/{cnt:,} rows  ({rate:,.0f}/s)", end="", flush=True)
    write_progress(config, state, {"next": a, "rows": rows_total, "expected": cnt, "done": True,
                                   "columns": cols, "finished": dt.datetime.now().isoformat()})
    print(f"\n[{state}] done: {rows_total:,} rows -> {out}")
