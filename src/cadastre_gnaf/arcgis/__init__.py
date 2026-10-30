"""Minimal ArcGIS REST client: paged, retrying, ObjectID-range queries."""

from cadastre_gnaf.arcgis.arcgis_get import arcgis_get
from cadastre_gnaf.arcgis.errors import ArcGISError
from cadastre_gnaf.arcgis.feature_count import feature_count
from cadastre_gnaf.arcgis.fetch_range import fetch_range
from cadastre_gnaf.arcgis.layer_info import layer_info
from cadastre_gnaf.arcgis.make_session import make_session
from cadastre_gnaf.arcgis.oid_bounds import oid_bounds

__all__ = ["ArcGISError", "arcgis_get", "feature_count", "fetch_range", "layer_info", "make_session",
           "oid_bounds"]
