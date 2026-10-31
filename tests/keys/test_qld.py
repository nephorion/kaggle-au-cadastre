from cadastre_gnaf.keys import keys_qld


def test_lot_plan():
    k = keys_qld({"lot": "66", "plan": "RP139841", "lotplan": "66RP139841"})
    assert k == {"key_lot_plan": "66/RP139841", "key_lotplan": "66RP139841"}


def test_missing_plan():
    assert keys_qld({"lot": "66"})["key_lot_plan"] is None
