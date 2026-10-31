import pytest

from cadastre_gnaf.gnaf import read_address_parcels, read_address_points
from cadastre_gnaf.linking import spatial_fallback_links

pytest.importorskip("geopandas")


def test_only_unlinked_addresses_are_spatially_joined(act_parcels, gnaf):
    addresses, points = read_address_parcels(gnaf, "ACT"), read_address_points(gnaf, "ACT")
    extra = spatial_fallback_links(act_parcels, addresses, points, linked_pids=["GAACT1", "GAACT2"])
    assert sorted(extra["address_detail_pid"]) == ["GAACT3", "GAACT5"]
    by_pid = extra.set_index("address_detail_pid")
    assert by_pid.loc["GAACT3", "source_oid"] == 2
    assert by_pid.loc["GAACT3", "legal_parcel_id"] == "CANB/BRAD/18/42"
    assert set(extra["method"]) == {"spatial_within"}
