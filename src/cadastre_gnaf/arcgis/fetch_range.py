from cadastre_gnaf.arcgis.arcgis_get import arcgis_get

MAX_SPLIT_DEPTH = 20


def fetch_range(session, url, oid, lo, hi, where="1=1", token=None, decimals=6, depth=0):
    """All features with lo <= OID < hi. Splits the range if the server truncates."""
    p = {"where": f"({where}) AND {oid} >= {lo} AND {oid} < {hi}", "outFields": "*",
         "returnGeometry": "true", "outSR": 4326, "geometryPrecision": decimals + 1}
    if token:
        p["token"] = token
    js = arcgis_get(session, url + "/query", p)
    feats = js.get("features", [])
    if js.get("exceededTransferLimit") and hi - lo > 1 and depth < MAX_SPLIT_DEPTH:
        mid = (lo + hi) // 2
        return (fetch_range(session, url, oid, lo, mid, where, token, decimals, depth + 1) +
                fetch_range(session, url, oid, mid, hi, where, token, decimals, depth + 1))
    return feats
