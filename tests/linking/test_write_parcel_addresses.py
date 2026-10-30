import pandas as pd

from cadastre_gnaf.constants import ADDRESS_COLUMNS
from cadastre_gnaf.linking import write_parcel_addresses

LINKS = pd.DataFrame({"address_detail_pid": ["GA1", "GA2", "GA1"], "legal_parcel_id": ["k", "k", "k"],
                      "source_oid": ["1", "1", "1"], "method": ["legal_parcel_id"] * 3})
ADDRESSES = pd.DataFrame({"address_detail_pid": ["GA1", "GA2"], "address_full": ["1 A ST", "2 A ST"],
                          "address_postcode": ["0800", "0800"], "address_lon": [149.5, 149.6]})


def test_left_join_one_row_per_parcel_and_address(act_parcels, tmp_path):
    out = tmp_path / "pa.csv"
    rows = write_parcel_addresses(act_parcels, LINKS, ADDRESSES, out, chunk=2)
    df = pd.read_csv(out, dtype=str, keep_default_na=False)
    # act_parcels: OID 1, 2, 1 -> OID 1 gets its two addresses (each time it appears), OID 2 gets none
    assert rows == len(df) == 5
    assert df["source_oid"].tolist() == ["1", "1", "2", "1", "1"]
    assert df["address_full"].tolist() == ["1 A ST", "2 A ST", "", "1 A ST", "2 A ST"]
    assert df["address_postcode"].tolist()[0] == "0800"
    assert df.loc[2, "address_detail_pid"] == "" and df.loc[0, "address_link_method"] == "legal_parcel_id"


def test_column_order_keeps_wkt_last(act_parcels, tmp_path):
    out = tmp_path / "pa.csv"
    write_parcel_addresses(act_parcels, LINKS, ADDRESSES, out)
    cols = pd.read_csv(out, nrows=0).columns.tolist()
    assert cols[:2] == ["state", "source_oid"] and cols[-1] == "wkt"
    assert cols[-1 - len(ADDRESS_COLUMNS):-1] == ADDRESS_COLUMNS


def test_parcels_without_any_links(act_parcels, tmp_path):
    out = tmp_path / "pa.csv"
    rows = write_parcel_addresses(act_parcels, LINKS.iloc[0:0], ADDRESSES.iloc[0:0], out)
    df = pd.read_csv(out)
    assert rows == 3 and df["address_detail_pid"].isna().all()
