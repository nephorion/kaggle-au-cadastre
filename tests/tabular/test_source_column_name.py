import pytest

from cadastre_gnaf.tabular import source_column_name


@pytest.mark.parametrize(("name", "expected"), [
    ("TENURE_TY", "src_tenure_ty"), ("parcel_spi", "src_parcel_spi"), ("GlobalID", "src_globalid"),
    ("Shape.STArea()", "src_shape_starea"), ("src_state", "src_state"),
])
def test_names(name, expected):
    assert source_column_name(name) == expected
