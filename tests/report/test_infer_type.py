import pytest

from cadastre_gnaf.report import infer_type


@pytest.mark.parametrize(("values", "expected"), [
    (["1", "22", ""], "integer"),
    (["1.5", "2"], "number"),
    (["1.0", "2.0"], "number"),
    (["2026-01-02", ""], "date"),
    (["abc", "1"], "string"),
    (["", ""], "string"),
    ([], "string"),
])
def test_infers(values, expected):
    assert infer_type(values) == expected
