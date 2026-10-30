import gzip

from cadastre_gnaf.report import count_rows


def test_counts_data_rows_not_lines(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text('a,b\n1,"two\nlines"\n2,x\n')
    assert count_rows(p) == 2


def test_header_only(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text("a,b\n")
    assert count_rows(p) == 0


def test_gzip(tmp_path):
    p = tmp_path / "a.csv.gz"
    with gzip.open(p, "wt") as f:
        f.write("a\n1\n2\n3\n")
    assert count_rows(p, chunk=2) == 3
