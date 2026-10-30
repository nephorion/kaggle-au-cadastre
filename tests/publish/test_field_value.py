import pandas as pd
import pytest

from cadastre_gnaf.publish import field_value

FRAME = pd.DataFrame({
    "a": ["x", "", "y"], "b": ["1", "2", ""], "code": ["A", "Z", ""], "num": ["17253.0", "", "x"],
    "day": ["2026-01-02", "3000-01-01", "bad"], "area": ["707 square metres", "1.5 hectares", "?"],
    "val": ["960.5", "2", "0"], "unit": ["Meters", "Hectare", ""], "flag": ["Y", "N", ""],
})


def values(spec, column=""):
    return field_value(FRAME, spec, column).tolist()


def test_plain_column_and_missing_column():
    assert values("a") == ["x", "", "y"]
    assert values("nope") == ["", "", ""]
    assert values(None) == ["", "", ""]


def test_const_prefix_join_first():
    assert values(("const", "lease")) == ["lease"] * 3
    assert values(("prefix", "DP", "b")) == ["DP1", "DP2", ""]
    assert values(("join", "/", ["a", "b"])) == ["x/1", "", ""]           # only when all parts are present
    assert values(("first", ["a", "b"])) == ["x", "2", "y"]


def test_replace():
    assert field_value(pd.DataFrame({"vf": ["1186:24", ""]}), ("replace", "vf", ":", "/")).tolist() == ["1186/24", ""]


def test_map_unlisted_codes():
    assert values(("map", "code", {"A": "current"})) == ["current", "", ""]
    assert values(("map", "code", {"A": "freehold"}), column="tenure") == ["freehold", "other", ""]


def test_int_and_date():
    assert values(("int", "num")) == ["17253", "", ""]
    assert values(("date", "day")) == ["2026-01-02", "", ""]               # 3000-01-01 = "still current"


def test_area_from_text_and_unit_column():
    assert values(("area", "area", None)) == ["707.00", "15000.00", ""]
    assert values(("area", "val", "unit")) == ["960.50", "20000.00", ""]   # empty unit = unknown -> null


def test_match_and_present():
    assert values(("match", "flag", r"^Y$")) == ["True", "False", ""]
    assert values(("present", "a")) == ["True", "False", "True"]


def test_unknown_spec():
    with pytest.raises(ValueError):
        values(("nope", "a"))
