import pytest

from cadastre_gnaf.keys import strip_zeros


@pytest.mark.parametrize(("raw", "expected"), [
    ("007", "7"), ("100", "100"), ("000", "0"), ("0", "0"), ("", ""), ("A01", "A01"),
])
def test_strip_zeros(raw, expected):
    assert strip_zeros(raw) == expected
