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


def test_degenerate_multipolygon_part_does_not_fail():
    # one part has too few points: GEOS's default repair raises "Overlay input is mixed-dimension" on it
    bad = "MULTIPOLYGON (((149 -35,149 -34.99,149.01 -34.99,149 -35)),((149.5 -35,149.5 -35,149.5 -35)))"
    m = geometry_measures(pd.Series([SQUARE, bad]))
    assert float(m.loc[0, "area_m2"]) > 0 and m.loc[1, "is_multipart"] == "True"


def test_unrepairable_geometry_gets_null_measures(monkeypatch):
    import shapely

    real = shapely.make_valid

    def flaky(g, **kw):
        if not hasattr(g, "__len__") and g.equals(shapely.from_wkt(BOWTIE)):
            raise shapely.errors.GEOSException("boom")
        if hasattr(g, "__len__"):
            raise shapely.errors.GEOSException("chunk fails")
        return real(g, **kw)

    monkeypatch.setattr(shapely, "make_valid", flaky)
    m = geometry_measures(pd.Series([SQUARE, BOWTIE]))
    assert float(m.loc[0, "area_m2"]) > 0 and m.loc[1, "area_m2"] == "" and m.loc[1, "is_multipart"] == ""
