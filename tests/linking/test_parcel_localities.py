import pandas as pd

from cadastre_gnaf.linking import parcel_localities

LOCALITIES = pd.DataFrame({"ADDRESS_DETAIL_PID": ["A", "B", "C", "D", "E"],
                           "LOCALITY_NAME": ["TURNER", "BRADDON", "BRADDON", "", "AINSLIE"]})


def test_most_common_locality_per_parcel():
    links = pd.DataFrame({"source_oid": ["1", "1", "1", "2", "3", "3"],
                          "address_detail_pid": ["A", "B", "C", "D", "A", "E"]})
    assert parcel_localities(links, LOCALITIES).to_dict() == {"1": "BRADDON", "3": "AINSLIE"}   # tie: A-Z


def test_no_links():
    links = pd.DataFrame(columns=["source_oid", "address_detail_pid"], dtype=str)
    assert parcel_localities(links, LOCALITIES).empty
