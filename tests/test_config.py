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


def test_staging_and_progress_under_work_dir():
    c = Config(out_dir=Path("o"), work_dir=Path("w"))
    assert c.staging_dir == Path("w") / "staging"
    assert c.progress_dir == Path("w") / "staging" / "_progress"


@pytest.mark.parametrize(("step", "download", "gnaf", "publish"), [
    ("all", True, True, True), ("download", True, False, False), ("gnaf", False, True, True),
    ("publish", False, False, True), ("docs", False, False, False),
])
def test_step_flags(step, download, gnaf, publish):
    c = Config(step=step)
    assert (c.do_download, c.do_gnaf, c.do_publish) == (download, gnaf, publish)
