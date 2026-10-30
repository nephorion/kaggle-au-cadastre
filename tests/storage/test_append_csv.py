import pandas as pd

from cadastre_gnaf.storage import append_csv


def test_first_write_then_append_in_column_order(tmp_path):
    path = tmp_path / "x.csv"
    append_csv(path, pd.DataFrame([{"b": 1, "a": 2}]), ["a", "b", "c"], first=True)
    append_csv(path, pd.DataFrame([{"a": 3, "extra": 9}]), ["a", "b", "c"], first=False)
    assert path.read_text().splitlines() == ["a,b,c", "2,1,", "3,,"]


def test_first_write_truncates(tmp_path):
    path = tmp_path / "x.csv"
    path.write_text("old\n")
    append_csv(path, pd.DataFrame([{"a": 1}]), ["a"], first=True)
    assert path.read_text().splitlines() == ["a", "1"]


def test_first_write_creates_folder(tmp_path):
    path = tmp_path / "new" / "x.csv"
    append_csv(path, pd.DataFrame([{"a": 1}]), ["a"], first=True)
    assert path.exists()


def test_gzip(tmp_path):
    path = tmp_path / "x.csv.gz"
    append_csv(path, pd.DataFrame([{"a": 1}]), ["a"], first=True, compression="gzip")
    append_csv(path, pd.DataFrame([{"a": 2}]), ["a"], first=False, compression="gzip")
    assert pd.read_csv(path)["a"].tolist() == [1, 2]
