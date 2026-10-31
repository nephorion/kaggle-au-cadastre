import json

from cadastre_gnaf.arcgis.arcgis_get import arcgis_get
from cadastre_gnaf.arcgis.errors import ArcGISError


def oid_bounds(session, url, oid, where="1=1", token=None, at_least=None):
    """Min/max ObjectID (optionally min OID >= at_least). Uses statistics, falls back to ID list."""
    w = where if at_least is None else f"({where}) AND {oid} >= {int(at_least)}"
    p = {"where": w, "returnGeometry": "false",
         "outStatistics": json.dumps([
             {"statisticType": "min", "onStatisticField": oid, "outStatisticFieldName": "mn"},
             {"statisticType": "max", "onStatisticField": oid, "outStatisticFieldName": "mx"}])}
    if token:
        p["token"] = token
    try:
        js = arcgis_get(session, url + "/query", p, retries=3)
        a = {k.lower(): v for k, v in js["features"][0]["attributes"].items()}
        return a.get("mn"), a.get("mx")
    except (ArcGISError, KeyError, IndexError, TypeError, AttributeError):
        p = {"where": w, "returnIdsOnly": "true"}
        if token:
            p["token"] = token
        ids = arcgis_get(session, url + "/query", p).get("objectIds") or []
        return (min(ids), max(ids)) if ids else (None, None)
