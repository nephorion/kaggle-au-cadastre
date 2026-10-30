from dataclasses import replace

import pandas as pd
import pytest

from cadastre_gnaf.download import load_local_state
from cadastre_gnaf.keys import keys_sa
from cadastre_gnaf.sources import Source
from cadastre_gnaf.storage import parcels_path, read_progress

gpd = pytest.importorskip("geopandas")
shapely_geometry = pytest.importorskip("shapely.geometry")

SOURCE = Source(url=None, keys=keys_sa, licence="test")


@pytest.fixture
def sa_file(tmp_path):
    box = shapely_geometry.box
    gdf = gpd.GeoDataFrame(
        {"PLAN_T": ["D", "D", "F"], "PLAN": ["10001", "10001", "2"], "PARCEL_T": ["A", "A", "Q"],
         "PARCEL": ["14", "15", "1"]},
        geometry=[box(138, -35, 138.001, -34.999), box(138.1, -35, 138.101, -34.999), None],
        crs=4326)
    path = tmp_path / "sa.geojson"
    gdf.to_file(path, driver="GeoJSON")
    return path


def test_loads_file_into_parcels_csv(config, sa_file):
    cfg = replace(config, states=("SA",))
    load_local_state(cfg, "SA", SOURCE, sa_file)
    df = pd.read_csv(parcels_path(cfg, "SA"))
    assert len(df) == 2                                         # null geometry dropped
    assert df["source_oid"].tolist() == [1, 2]
    assert df["key_plant_plan_parcelt_parcel"].tolist() == ["D/10001/A/14", "D/10001/A/15"]
    assert df.loc[0, "wkt"].startswith("POLYGON")
    assert 138 < df.loc[0, "point_lon"] < 138.001
    assert read_progress(cfg, "SA") == {"rows": 2, "expected": 2, "done": True,
                                         "columns": list(df.columns), "source": str(sa_file)}


def test_without_wkt(config, sa_file):
    cfg = replace(config, include_wkt=False)
    load_local_state(cfg, "SA", SOURCE, sa_file)
    assert "wkt" not in pd.read_csv(parcels_path(cfg, "SA")).columns
