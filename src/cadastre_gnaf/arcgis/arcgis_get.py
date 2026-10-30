import random
import time

import requests

from cadastre_gnaf.arcgis.errors import ArcGISError

RETRY_STATUS = (429, 500, 502, 503, 504)


def arcgis_get(session, url, params, retries=6, timeout=180, sleep=time.sleep):
    """GET (POST for long queries) with retries; raises on ArcGIS JSON errors after retries."""
    params = {"f": "json", **params}
    last = None
    for attempt in range(retries):
        try:
            long_q = len(str(params)) > 1500
            r = (session.post(url, data=params, timeout=timeout) if long_q
                 else session.get(url, params=params, timeout=timeout))
            if r.status_code in RETRY_STATUS:
                raise ArcGISError(f"HTTP {r.status_code}")
            r.raise_for_status()
            js = r.json()
            if isinstance(js, dict) and "error" in js:
                raise ArcGISError(js["error"])
            return js
        except (requests.RequestException, ValueError, ArcGISError) as e:
            last = e
            sleep(min(60, 2 ** attempt + random.random()))
    raise ArcGISError(f"{url} failed after {retries} tries: {last}")
