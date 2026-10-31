import pyarrow as pa
import pytest

from cadastre_gnaf.publish import arrow_type


@pytest.mark.parametrize(("kind", "expected"), [
    ("integer", pa.int64()), ("number", pa.float64()), ("boolean", pa.bool_()), ("date", pa.date32()),
    ("string", pa.string()), ("list<string>", pa.list_(pa.string())), (None, pa.string()), ("odd", pa.string()),
])
def test_maps_kinds(kind, expected):
    assert arrow_type(kind) == expected
