"""Step 1: download each state's parcels into a flat CSV."""

from cadastre_gnaf.download.download_arcgis_state import download_arcgis_state
from cadastre_gnaf.download.fetch_in_order import fetch_in_order
from cadastre_gnaf.download.load_local_state import load_local_state
from cadastre_gnaf.download.page_size import page_size
from cadastre_gnaf.download.run_downloads import run_downloads

__all__ = ["download_arcgis_state", "fetch_in_order", "load_local_state", "page_size", "run_downloads"]
