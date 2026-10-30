import pandas as pd

from cadastre_gnaf.constants import HARMONISED_COLUMNS
from cadastre_gnaf.publish import harmonised_columns
from cadastre_gnaf.publish.field_map import FIELD_MAP

SQUARE = "POLYGON ((149 -35,149 -34.999,149.001 -34.999,149.001 -35,149 -35))"


def test_every_state_has_a_field_map_using_only_known_columns():
    for state, fields in FIELD_MAP.items():
        assert set(fields) <= set(HARMONISED_COLUMNS), state


def test_qld_example():
    frame = pd.DataFrame({"lot": ["4"], "plan": ["SE1"], "lotplan": ["4SE1"], "tenure": ["Reserve"],
                          "statedarea": ["2"], "statedareaunit": ["Hectare"], "locality": ["Strathmore"],
                          "parcel_state": ["Created"], "wkt": [SQUARE]})
    h = harmonised_columns(frame, "QLD").iloc[0]
    assert list(h.index) == list(HARMONISED_COLUMNS)
    assert (h["lot"], h["plan"], h["parcel_label"]) == ("4", "SE1", "4SE1")
    assert (h["tenure"], h["status"]) == ("crown", "current")
    assert h["stated_area_m2"] == "20000.00" and h["locality"] == "STRATHMORE"
    assert float(h["area_m2"]) > 0 and h["is_multipart"] == "False"
    assert h["title_ref"] == "" and h["is_road"] == ""                    # QLD has neither


def test_gnaf_locality_wins_over_source():
    frame = pd.DataFrame({"locality": ["Strathmore", "Collins"], "gnaf_locality": ["CROYDON", ""]})
    assert harmonised_columns(frame, "QLD")["locality"].tolist() == ["CROYDON", "COLLINS"]


def test_state_without_attributes_gets_geometry_only():
    h = harmonised_columns(pd.DataFrame({"view_scale": ["4K"], "wkt": [SQUARE]}), "WA").iloc[0]
    assert float(h["area_m2"]) > 0 and h["lot"] == "" and h["status"] == ""
