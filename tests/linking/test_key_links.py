import pandas as pd

from cadastre_gnaf.linking import key_links


def test_links_addresses_of_matched_parcels_only():
    addresses = pd.DataFrame({"ADDRESS_DETAIL_PID": ["G1", "G2", "G3"],
                              "LEGAL_PARCEL_ID": ["1/DP1", "1/DP1", "2/DP2"],
                              "key": ["1/DP1", "1/DP1", "2/DP2"]})
    chosen = pd.Series({"10": "1/DP1", "20": "2/DP2"})
    matched = pd.Series({"10": True, "20": False})
    links = key_links(addresses, chosen, matched)
    assert list(links.columns) == ["address_detail_pid", "legal_parcel_id", "source_oid", "method"]
    assert links["address_detail_pid"].tolist() == ["G1", "G2"]
    assert set(links["source_oid"]) == {"10"} and set(links["method"]) == {"legal_parcel_id"}
