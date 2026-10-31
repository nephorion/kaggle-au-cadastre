from cadastre_gnaf.keys import keys_nsw


def test_lot_and_plan_number_without_section():
    k = keys_nsw({"lotnumber": 13, "sectionnumber": None, "plannumber": 31993, "planlabel": "DP31993"})
    assert k["key_lot_sec_plannum"] == "13/31993"
    assert k["key_lot_label"] == "13/DP31993"
    assert k["key_lot_sec_label"] == "13//DP31993"


def test_lot_section_plan_number():
    k = keys_nsw({"lotnumber": "11", "sectionnumber": "C", "plannumber": 3625})
    assert k["key_lot_sec_plannum"] == "11/C/3625"


def test_lotidstring_normalised():
    assert keys_nsw({"lotidstring": "1//dp 12345"})["key_lotidstring"] == "1//DP12345"


def test_empty_attributes_give_no_keys():
    assert set(keys_nsw({}).values()) == {None}
