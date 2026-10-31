from cadastre_gnaf.keys import keys_wa


def test_pi_parcel_and_lot():
    assert keys_wa({"pi_parcel": "S030337", "lot_number": 1}) == {"key_piparcel_lot": "S030337/1"}


def test_alternative_field_names():
    assert keys_wa({"PIPARCEL": "P1", "LOTNUMBER": "2"}) == {"key_piparcel_lot": "P1/2"}


def test_public_layer_without_attributes():
    assert keys_wa({}) == {"key_piparcel_lot": None}
