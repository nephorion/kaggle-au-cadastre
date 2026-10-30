"""Step 1: download each state's parcels into a flat CSV."""

from cadastre_gnaf.download.download_arcgis_state import download_arcgis_state
from cadastre_gnaf.download.load_local_state import load_local_state
from cadastre_gnaf.download.page_ranges import page_ranges
from cadastre_gnaf.download.page_size import page_size
from cadastre_gnaf.download.run_downloads import run_downloads

__all__ = ["download_arcgis_state", "load_local_state", "page_ranges", "page_size", "run_downloads"]
