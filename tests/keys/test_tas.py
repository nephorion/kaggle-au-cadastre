from cadastre_gnaf.keys import keys_tas


def test_volume_folio():
    assert keys_tas({"VOLUME": "158882", "FOLIO": 1})["key_vol_folio"] == "158882/1"


def test_leading_zeros_stripped_only_in_main_key():
    k = keys_tas({"VOLUME": "058882", "FOLIO": "01"})
    assert k == {"key_vol_folio": "58882/1", "key_vol_folio_raw": "058882/01"}


def test_missing_folio():
    assert keys_tas({"VOLUME": "1"}) == {"key_vol_folio": None, "key_vol_folio_raw": None}
