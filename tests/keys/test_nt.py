from cadastre_gnaf.keys import keys_nt


def test_location_parcel_lto():
    k = keys_nt({"PAR_LOC": "550", "PAR_PAR": "03252", "PAR_LTO": "X"})
    assert k == {"key_loc_par_lto": "550/3252/X", "key_loc_lto_par": "550/X/3252"}


def test_lto_optional():
    k = keys_nt({"PAR_LOC": "550", "PAR_PAR": "3252"})
    assert k == {"key_loc_par_lto": "550/3252/", "key_loc_lto_par": "550//3252"}


def test_parcel_required():
    assert set(keys_nt({"PAR_LOC": "550"}).values()) == {None}
