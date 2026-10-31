from pathlib import Path

import pytest

from cadastre_gnaf.cli import parse_config
from cadastre_gnaf.config import Config


def test_defaults_match_config_defaults():
    assert parse_config([], environ={}) == Config()


def test_tokens_from_environment_with_command_line_winning():
    c = parse_config(["--token", "WA=cli"], environ={"CADASTRE_TOKEN_wa": "env", "CADASTRE_TOKEN_NSW": "n",
                                                     "CADASTRE_TOKEN_VIC": "", "OTHER": "x"})
    assert c.arcgis_tokens == {"WA": "cli", "NSW": "n"}


def test_maps_arguments():
    c = parse_config(["--states", "nsw", "--no-wkt", "--gnaf-dir", "g", "--spatial-join", "wa", "act",
                      "--local", "sa=/x.shp", "--token", "wa=t", "--kaggle-id", "me/ds",
                      "--gnaf-kaggle-id", "me/gnaf"], environ={})
    assert c.states == ("NSW",) and c.include_wkt is False
    assert c.gnaf_dir == Path("g")
    assert c.spatial_join_states == ("WA", "ACT")
    assert c.local_sources == {"SA": "/x.shp"} and c.arcgis_tokens == {"WA": "t"}
    assert c.kaggle_id == "me/ds" and c.gnaf_kaggle_id == "me/gnaf"


def test_bad_pair_exits_with_usage_error(capsys):
    with pytest.raises(SystemExit) as e:
        parse_config(["--local", "SA"])
    assert e.value.code == 2
    assert "STATE=VALUE" in capsys.readouterr().err
