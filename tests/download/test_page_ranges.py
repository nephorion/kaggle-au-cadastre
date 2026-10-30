from cadastre_gnaf.download import page_ranges


def test_consecutive_ranges():
    assert page_ranges(10, 5, 3) == [(10, 15), (15, 20), (20, 25)]


def test_zero_count():
    assert page_ranges(1, 100, 0) == []
