from pathlib import Path

import pytest

from cadastre_gnaf.config import Config
from cadastre_gnaf.constants import DEFAULT_STATES


def test_defaults():
    c = Config()
    assert c.states == DEFAULT_STATES
    assert c.include_wkt and not c.compress
    assert c.spatial_join_states == ("WA",)


def test_csv_extension_and_compression():
    assert (Config().csv_ext, Config().compression) == (".csv", None)
    assert (Config(compress=True).csv_ext, Config(compress=True).compression) == (".csv.gz", "gzip")


def test_progress_dir_under_out_dir():
    assert Config(out_dir=Path("x")).progress_dir == Path("x") / "_progress"


@pytest.mark.parametrize(("step", "download", "gnaf", "addresses"), [
    ("all", True, True, True), ("download", True, False, False), ("gnaf", False, True, True),
    ("addresses", False, False, True), ("docs", False, False, False),
])
def test_step_flags(step, download, gnaf, addresses):
    c = Config(step=step)
    assert (c.do_download, c.do_gnaf, c.do_addresses) == (download, gnaf, addresses)
