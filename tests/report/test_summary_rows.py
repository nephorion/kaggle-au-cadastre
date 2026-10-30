import json
from dataclasses import replace

from cadastre_gnaf.report import summary_rows
from cadastre_gnaf.sources import Source
from cadastre_gnaf.storage import write_progress

SOURCES = {"WEB": Source(url="http://web", keys=dict, licence="CC BY"),
           "LOC": Source(url=None, keys=dict, licence="paid"),
           "NO": Source(url=None, keys=dict, licence="paid")}


def test_one_row_per_state(config):
    cfg = replace(config, states=("WEB", "LOC", "NO"), local_sources={"LOC": "/data/loc.shp"})
    write_progress(cfg, "WEB", {"expected": 10})
    summaries = [{"state": "WEB", "parcels": 9, "parcels_with_gnaf_key_match": 8, "gnaf_addresses": 20,
                  "address_link_rate": 0.9, "key_match": {"key_a": "8/9"}}]
    web, loc, no = summary_rows(cfg, SOURCES, summaries)
    assert web == {"state": "WEB", "source": "http://web", "features_expected": 10, "parcels_written": 9,
                   "parcels_matching_gnaf_key": 8, "gnaf_addresses": 20, "address_link_rate": 0.9,
                   "key_match_by_candidate": json.dumps({"key_a": "8/9"}), "licence": "CC BY"}
    assert loc["source"] == "/data/loc.shp" and loc["parcels_written"] is None
    assert no["source"] == "not available (licensed)"


def test_uses_saved_gnaf_figures_for_states_not_in_this_run(config):
    write_progress(config, "WEB", {"expected": 10, "gnaf": {"state": "WEB", "parcels": 7}})
    web, loc, no = summary_rows(replace(config, states=("LOC",)), SOURCES, [])
    assert web["parcels_written"] == 7 and web["features_expected"] == 10
    assert loc["parcels_written"] is None
