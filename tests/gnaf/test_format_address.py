import pandas as pd

from cadastre_gnaf.gnaf import format_address


def fmt(**cols):
    return format_address(pd.DataFrame({k: [v] for k, v in cols.items()}), "NSW").iloc[0].to_dict()


def test_full_address_with_flat_level_and_building():
    a = fmt(BUILDING_NAME="PARK  AVENUE", FLAT_TYPE_CODE="UNIT", FLAT_NUMBER="2", FLAT_NUMBER_SUFFIX="B",
            LEVEL_TYPE_CODE="L", LEVEL_NUMBER="3", NUMBER_FIRST="134", STREET_NAME="ARANDA",
            STREET_TYPE_CODE="STREET", LOCALITY_NAME="BELCONNEN", POSTCODE="2614")
    assert a["address_full"] == "PARK AVENUE, UNIT 2B, L 3, 134 ARANDA STREET, BELCONNEN NSW 2614"
    assert (a["address_flat"], a["address_level"], a["address_number"]) == ("UNIT 2B", "L 3", "134")


def test_number_range_prefix_and_suffix():
    a = fmt(NUMBER_FIRST_PREFIX="A", NUMBER_FIRST="10", NUMBER_LAST="14", NUMBER_LAST_SUFFIX="C",
            STREET_NAME="HIGH", STREET_TYPE_CODE="ROAD", STREET_SUFFIX_CODE="N")
    assert a["address_number"] == "A10-14C" and a["address_street"] == "HIGH ROAD N"


def test_lot_number_when_no_street_number():
    a = fmt(LOT_NUMBER="7", STREET_NAME="RIVER", STREET_TYPE_CODE="ROAD", LOCALITY_NAME="BOURKE")
    assert a["address_full"] == "LOT 7 RIVER ROAD, BOURKE NSW"


def test_missing_values_and_columns():
    a = fmt(NUMBER_FIRST=None, STREET_NAME=None, LOCALITY_NAME="X")
    assert a["address_full"] == "X NSW" and a["address_flat"] == "" and a["address_number"] == ""
