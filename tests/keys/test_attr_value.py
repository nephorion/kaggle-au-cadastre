import math

import pytest

from cadastre_gnaf.keys import attr_value


def test_exact_name():
    assert attr_value({"lot": "12"}, "lot") == "12"


@pytest.mark.parametrize("attrs", [{"lot": "1"}, {"LOT": "1"}])
def test_case_insensitive(attrs):
    assert attr_value(attrs, "Lot") == "1"


def test_first_matching_name_wins():
    assert attr_value({"b": "2", "a": "1"}, "a", "b") == "1"
    assert attr_value({"b": "2"}, "a", "b") == "2"


def test_integral_float_becomes_int():
    assert attr_value({"x": 13.0}, "x") == "13"


def test_non_integral_float_kept():
    assert attr_value({"x": 1.5}, "x") == "1.5"


@pytest.mark.parametrize("v", [math.nan, "", "  ", "None", "null", "NaN"])
def test_blank_like_values_are_empty(v):
    assert attr_value({"x": v}, "x") == ""


def test_none_is_skipped_for_next_name():
    assert attr_value({"a": None, "b": "ok"}, "a", "b") == "ok"


def test_missing_is_empty():
    assert attr_value({}, "x") == ""


def test_strips_whitespace():
    assert attr_value({"x": "  DP1 "}, "x") == "DP1"
