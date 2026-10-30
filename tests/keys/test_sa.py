from cadastre_gnaf.keys import keys_sa


def test_plan_and_parcel():
    k = keys_sa({"PLAN_T": "D", "PLAN": "10001", "PARCEL_T": "A", "PARCEL": "14", "DCDBID": "d10001 a14"})
    assert k == {"key_plant_plan_parcelt_parcel": "D/10001/A/14", "key_dcdbid": "D10001A14"}


def test_incomplete_plan():
    assert keys_sa({"PLAN_T": "D", "PLAN": "10001"})["key_plant_plan_parcelt_parcel"] is None
