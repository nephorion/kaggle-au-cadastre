import pandas as pd
import pytest

from cadastre_gnaf.storage import parcels_path


def square(x0, y0):
    return f"POLYGON (({x0} {y0},{x0} {y0 + 1},{x0 + 1} {y0 + 1},{x0 + 1} {y0},{x0} {y0}))"


@pytest.fixture
def act_parcels(config):
    """ACT parcels CSV: OID 1 matches G-NAF by key, OID 2 does not; OID 1 appears twice."""
    rows = [
        {"state": "ACT", "source_oid": 1, "key_dist_div_sec_blk": "CANB/BRAD/18/41", "key_dist_blk": "CANB/41",
         "point_lon": 149.5, "point_lat": -34.5, "BLOCK": "41", "wkt": square(149, -35)},
        {"state": "ACT", "source_oid": 2, "key_dist_div_sec_blk": "CANB/BRAD/18/99", "key_dist_blk": "CANB/99",
         "point_lon": 150.5, "point_lat": -34.5, "BLOCK": "99", "wkt": square(150, -35)},
        {"state": "ACT", "source_oid": 1, "key_dist_div_sec_blk": "CANB/BRAD/18/41", "key_dist_blk": "CANB/41",
         "point_lon": 149.5, "point_lat": -34.5, "BLOCK": "41", "wkt": square(149, -35)},
    ]
    path = parcels_path(config, "ACT")
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path
