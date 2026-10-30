import pytest

from cadastre_gnaf.tabular import epoch_ms_to_date


def test_converts_epoch_ms_utc():
    assert epoch_ms_to_date(1_700_000_000_000) == "2023-11-14"
    assert epoch_ms_to_date(0) == "1970-01-01"


@pytest.mark.parametrize("v", [None, "", "not a date"])
def test_passthrough(v):
    assert epoch_ms_to_date(v) == v


def test_out_of_range_passthrough():
    assert epoch_ms_to_date(10**30) == 10**30
