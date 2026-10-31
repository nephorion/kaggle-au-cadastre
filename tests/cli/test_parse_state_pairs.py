import pytest

from cadastre_gnaf.cli import parse_state_pairs


def test_parses_and_uppercases_state():
    assert parse_state_pairs(["sa=/data/a=b.shp", "NT=x"]) == {"SA": "/data/a=b.shp", "NT": "x"}


def test_empty():
    assert parse_state_pairs([]) == {}


def test_rejects_missing_equals():
    with pytest.raises(ValueError, match="STATE=VALUE"):
        parse_state_pairs(["SA"])
