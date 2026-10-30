from pathlib import Path

import pytest

from cadastre_gnaf.cli import parse_config
from cadastre_gnaf.config import Config


def test_defaults_match_config_defaults():
    assert parse_config([]) == Config()


def test_maps_arguments():
    c = parse_config(["--states", "nsw", "--no-wkt", "--gnaf-dir", "g", "--spatial-join", "wa", "act",
                      "--local", "sa=/x.shp", "--token", "wa=t"])
    assert c.states == ("NSW",) and c.include_wkt is False
    assert c.gnaf_dir == Path("g")
    assert c.spatial_join_states == ("WA", "ACT")
    assert c.local_sources == {"SA": "/x.shp"} and c.arcgis_tokens == {"WA": "t"}


def test_bad_pair_exits_with_usage_error(capsys):
    with pytest.raises(SystemExit) as e:
        parse_config(["--local", "SA"])
    assert e.value.code == 2
    assert "STATE=VALUE" in capsys.readouterr().err
