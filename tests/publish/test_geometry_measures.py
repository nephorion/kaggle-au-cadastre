import pandas as pd

from cadastre_gnaf.publish import geometry_measures

# ~1 km x ~1 km near Canberra (0.01° lon x 0.009° lat)
SQUARE = "POLYGON ((149 -35,149 -34.991,149.0109 -34.991,149.0109 -35,149 -35))"
TWO = "MULTIPOLYGON (((149 -35,149 -34.999,149.001 -34.999,149 -35)),((150 -35,150 -34.999,150.001 -34.999,150 -35)))"
BOWTIE = "POLYGON ((149 -35,149.01 -34.99,149.01 -35,149 -34.99,149 -35))"


def test_area_perimeter_and_parts():
    m = geometry_measures(pd.Series([SQUARE, TWO, "", "not wkt"]))
    area, perim = float(m.loc[0, "area_m2"]), float(m.loc[0, "perimeter_m"])
    assert 950_000 < area < 1_050_000 and 3_900 < perim < 4_100
    assert m["is_multipart"].tolist() == ["False", "True", "", ""]
    assert m.loc[2, "area_m2"] == "" and m.loc[3, "area_m2"] == ""


def test_invalid_polygon_repaired():
    assert float(geometry_measures(pd.Series([BOWTIE]))["area_m2"][0]) > 0


def test_no_geometry():
    m = geometry_measures(pd.Series(["", None]))
    assert m.to_dict("list") == {"area_m2": ["", ""], "perimeter_m": ["", ""], "is_multipart": ["", ""]}
