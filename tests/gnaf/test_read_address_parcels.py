import pandas as pd

from cadastre_gnaf.gnaf import read_address_parcels


def test_live_addresses_with_normalised_key(gnaf):
    df = read_address_parcels(gnaf, "ACT").set_index("ADDRESS_DETAIL_PID")
    assert list(df.index) == ["GAACT1", "GAACT2", "GAACT3", "GAACT5"]
    assert df.loc["GAACT1", "key"] == "CANB/BRAD/18/41"
    assert df.loc["GAACT1", "LEGAL_PARCEL_ID"] == " CANB/BRAD/18/41 "
    assert pd.isna(df.loc["GAACT5", "key"])
