from cadastre_gnaf.gnaf import read_address_localities


def test_live_addresses_with_locality_names(gnaf):
    df = read_address_localities(gnaf, "ACT").set_index("ADDRESS_DETAIL_PID")["LOCALITY_NAME"]
    assert df.to_dict() == {"GAACT1": "BRADDON", "GAACT2": "BRADDON", "GAACT3": "BRADDON", "GAACT5": ""}
