from cadastre_gnaf.arcgis.arcgis_get import arcgis_get


def feature_count(session, url, where="1=1", token=None):
    """Number of features matching `where` (0 if the server does not say)."""
    p = {"where": where, "returnCountOnly": "true"}
    if token:
        p["token"] = token
    return arcgis_get(session, url + "/query", p).get("count") or 0
