import importlib
from dataclasses import replace

import pandas as pd

from cadastre_gnaf.linking import run_parcel_addresses
from cadastre_gnaf.storage import links_path, parcel_addresses_path

mod = importlib.import_module("cadastre_gnaf.linking.run_parcel_addresses")


def write_links(config):
    pd.DataFrame({"address_detail_pid": ["GAACT1", "GAACT3"], "legal_parcel_id": ["a", "b"],
                  "source_oid": ["1", "2"], "method": ["legal_parcel_id", "spatial_within"]}).to_csv(
        links_path(config, "ACT"), index=False)


def test_writes_parcels_with_addresses(config, act_parcels, gnaf, capsys):
    write_links(config)
    run_parcel_addresses(replace(config, states=("ACT", "NSW")), None, gnaf)
    df = pd.read_csv(parcel_addresses_path(config, "ACT"))
    assert df["address_full"].tolist() == ["UNIT 1, 12 LONSDALE STREET, BRADDON ACT 2612",
                                           "14 LONSDALE STREET, BRADDON ACT 2612",
                                           "UNIT 1, 12 LONSDALE STREET, BRADDON ACT 2612"]
    assert df["address_link_method"].tolist()[1] == "spatial_within"
    assert "3 parcel/address rows" in capsys.readouterr().out
    assert not parcel_addresses_path(config, "NSW").exists()


def test_skips_state_without_links(config, act_parcels, gnaf):
    run_parcel_addresses(config, None, gnaf)
    assert not parcel_addresses_path(config, "ACT").exists()


def test_failure_is_reported_not_raised(config, act_parcels, gnaf, monkeypatch, capsys):
    write_links(config)
    monkeypatch.setattr(mod, "read_addresses", lambda *a: (_ for _ in ()).throw(RuntimeError("bad")))
    run_parcel_addresses(config, None, gnaf)
    assert "parcels with addresses FAILED" in capsys.readouterr().out


def test_opens_gnaf_when_not_given(config, monkeypatch):
    opened = []
    monkeypatch.setattr(mod, "open_gnaf", lambda cfg, session: opened.append(1) or "G")
    run_parcel_addresses(config, None)
    assert opened == [1]
