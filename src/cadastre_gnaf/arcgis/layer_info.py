from cadastre_gnaf.arcgis.arcgis_get import arcgis_get
from cadastre_gnaf.arcgis.errors import ArcGISError


def layer_info(session, url, token=None):
    """Layer metadata and the name of its ObjectID field."""
    info = arcgis_get(session, url, {"token": token} if token else {})
    oid = info.get("objectIdField") or next(
        (f["name"] for f in info.get("fields", []) if f.get("type") == "esriFieldTypeOID"), None)
    if not oid:
        raise ArcGISError(f"No ObjectID field found for {url}")
    return info, oid
