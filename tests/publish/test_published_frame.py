import pandas as pd

from cadastre_gnaf.constants import HARMONISED_COLUMNS, LEADING_COLUMNS
from cadastre_gnaf.publish import published_frame

LEADING = {c: ["x"] for c in LEADING_COLUMNS}


def test_layout_drops_and_renames():
    frame = pd.DataFrame({**LEADING, "key_spi": ["k"], "OBJECTID": ["1"], "Shape__Area": ["9"], "shape_Length": ["9"],
                          "parcel_spi": ["1\\PS1"], "TENURE_TY": ["t"], "src_state": ["s"], "gnaf_locality": [""],
                          "wkt": [""]})
    out = published_frame(frame, "VIC")
    assert out.columns.tolist() == [*LEADING_COLUMNS, *HARMONISED_COLUMNS, "src_parcel_spi", "src_tenure_ty",
                                    "src_state", "wkt"]
    assert out.loc[0, "parcel_label"] == "1\\PS1" and out.loc[0, "src_parcel_spi"] == "1\\PS1"


def test_every_state_same_leading_and_harmonised_columns():
    shared = [*LEADING_COLUMNS, *HARMONISED_COLUMNS]
    for state, extra in (("NSW", "lotnumber"), ("TAS", "VOLUME"), ("WA", "view_scale")):
        cols = published_frame(pd.DataFrame({**LEADING, extra: ["1"], "wkt": [""]}), state).columns.tolist()
        assert cols[:len(shared)] == shared and cols[-1] == "wkt"


def test_header_only_frame():
    frame = pd.DataFrame(columns=[*LEADING_COLUMNS, "lot", "wkt"], dtype=str)
    out = published_frame(frame, "QLD")
    assert out.empty and "src_lot" in out.columns
