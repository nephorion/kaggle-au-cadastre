import pytest

from cadastre_gnaf.gnaf import GnafSource, read_addresses


def test_live_addresses_with_names_and_geocode(gnaf):
    a = read_addresses(gnaf, "ACT").set_index("address_detail_pid")
    assert list(a.index) == ["GAACT1", "GAACT2", "GAACT3", "GAACT5"]          # GAACT4 is retired
    assert a.loc["GAACT1", "address_full"] == "UNIT 1, 12 LONSDALE STREET, BRADDON ACT 2612"
    assert a.loc["GAACT3", "address_full"] == "14 LONSDALE STREET, BRADDON ACT 2612"
    assert (a.loc["GAACT1", "address_lon"], a.loc["GAACT1", "address_lat"]) == (149.5, -34.5)
    assert a.loc["GAACT5", "address_full"] == "ACT"


def test_limited_to_pids(gnaf):
    assert read_addresses(gnaf, "ACT", ["GAACT2", "GAACT9"])["address_detail_pid"].tolist() == ["GAACT2"]


def test_address_without_geocode_is_kept(gnaf_dir):
    a = read_addresses(GnafSource(root=gnaf_dir), "ACT", ["GAACT5"])
    assert len(a) == 1


@pytest.mark.parametrize("pids", [[], ["nope"]])
def test_no_matching_pids(gnaf, pids):
    assert read_addresses(gnaf, "ACT", pids).empty
