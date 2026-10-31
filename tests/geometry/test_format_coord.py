import pytest

from cadastre_gnaf.geometry.format_coord import format_coord


@pytest.mark.parametrize(("v", "d", "expected"), [
    (151.2, 6, "151.2"), (151.0, 6, "151"), (-33.1234567, 6, "-33.123457"), (0.0, 6, "0"), (12.5, 0, "12"),
])
def test_format_coord(v, d, expected):
    assert format_coord(v, d) == expected
