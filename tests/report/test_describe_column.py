import pytest

from cadastre_gnaf.report import describe_column

FIELDS = {"PLAN": {"name": "PLAN", "alias": "Plan number", "type": "esriFieldTypeString"},
          "LOT": {"name": "LOT", "alias": "lot", "type": "esriFieldTypeInteger"},
          "EDITED": {"name": "EDITED", "type": "esriFieldTypeDate"},
          "wkt": {"name": "wkt", "alias": "Source WKT", "type": "esriFieldTypeString"}}


@pytest.mark.parametrize(("column", "kind"), [("state", "string"), ("source_oid", "integer"),
                                              ("gnaf_key_matched", "boolean"), ("point_lat", "number")])
def test_own_columns(column, kind):
    assert describe_column(column, "ACT", FIELDS)[0] == kind


def test_key_columns():
    kind, text = describe_column("key_lot_plan", "QLD", {})
    assert kind == "string" and "66/RP139841" in text
    assert describe_column("key_new", "QLD", {}) == ("string", "Candidate G-NAF `LEGAL_PARCEL_ID` key.")


def test_source_field_with_alias():
    assert describe_column("PLAN", "QLD", FIELDS) == ("string", "QLD source attribute `PLAN`: Plan number.")


def test_alias_equal_to_name_is_omitted():
    assert describe_column("LOT", "QLD", FIELDS) == ("integer", "QLD source attribute `LOT`.")


def test_date_field():
    kind, text = describe_column("EDITED", "QLD", FIELDS)
    assert kind == "date" and "epoch milliseconds" in text


def test_prefixed_source_field_uses_original_name():
    assert describe_column("src_wkt", "QLD", FIELDS) == ("string", "QLD source attribute `wkt`: Source WKT.")


def test_unknown_field_type_left_for_inference():
    assert describe_column("OTHER", "QLD", FIELDS) == (None, "QLD source attribute `OTHER`.")


def test_harmonised_columns():
    assert describe_column("area_m2", "QLD", {})[0] == "number"
    assert describe_column("tenure", "QLD", {})[0] == "string"


def test_src_prefixed_snake_case_names():
    fields = {"TENURE_TY": {"name": "TENURE_TY", "alias": "Tenure Type", "type": "esriFieldTypeString"}}
    expected = ("string", "TAS source attribute `TENURE_TY`: Tenure Type.")
    assert describe_column("src_tenure_ty", "TAS", fields) == expected
    assert describe_column("src_unknown", "TAS", fields) == (None, "TAS source attribute `unknown`.")
