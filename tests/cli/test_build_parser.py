from cadastre_gnaf.cli import build_parser
from cadastre_gnaf.constants import DEFAULT_STATES


def test_defaults():
    a = build_parser().parse_args([])
    assert a.states == list(DEFAULT_STATES) and a.step == "all"
    assert a.workers == 4 and a.decimals == 6 and a.page_size is None
    assert a.spatial_join == ["WA"] and a.local == [] and a.token == []
    assert not (a.compress or a.no_wkt or a.force)
    assert a.kaggle_id == "your-kaggle-username/australian-cadastre-gnaf"
    assert a.gnaf_kaggle_id == "museofnephorion/australian-addresses-gnaf"


def test_all_options():
    a = build_parser().parse_args([
        "--states", "nsw", "VIC", "--step", "download", "--out", "o", "--work", "w", "--compress", "--no-wkt",
        "--decimals", "4", "--workers", "8", "--page-size", "500", "--force", "--gnaf-dir", "g",
        "--gnaf-zip-url", "http://z", "--spatial-join", "--local", "SA=/x", "--token", "WA=t", "--kaggle-id", "me/d"])
    assert a.states == ["nsw", "VIC"] and a.step == "download" and a.compress and a.no_wkt
    assert a.kaggle_id == "me/d" and build_parser().parse_args(["--step", "docs"]).step == "docs"
    assert (a.decimals, a.workers, a.page_size) == (4, 8, 500)
    assert a.spatial_join == [] and a.local == ["SA=/x"] and a.token == ["WA=t"]
