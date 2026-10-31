import datetime as dt

import pyarrow as pa

from cadastre_gnaf.publish import to_arrow


def test_integer():
    a = to_arrow(["1", "", "510361.0", "2.5", "x"], "integer")
    assert a.type == pa.int64() and a.to_pylist() == [1, None, 510361, None, None]


def test_number():
    assert to_arrow(["1.5", "", "-2", "nan?"], "number").to_pylist() == [1.5, None, -2.0, None]


def test_boolean():
    assert to_arrow(["True", "false", "", "maybe"], "boolean").to_pylist() == [True, False, None, None]


def test_date_keeps_far_future_dates():
    a = to_arrow(["2026-01-02", "3000-01-01", "", "bad"], "date")
    assert a.type == pa.date32() and a.to_pylist() == [dt.date(2026, 1, 2), dt.date(3000, 1, 1), None, None]


def test_list_of_strings():
    a = to_arrow(["GA1|GA2", "", "GA3"], "list<string>")
    assert a.type == pa.list_(pa.string()) and a.to_pylist() == [["GA1", "GA2"], None, ["GA3"]]


def test_string_and_unknown_kinds():
    assert to_arrow(["a", ""], "string").to_pylist() == ["a", None]
    assert to_arrow(["0800", ""], None).to_pylist() == ["0800", None]
