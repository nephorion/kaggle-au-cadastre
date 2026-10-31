from cadastre_gnaf.download import page_size


def test_requested_size_wins():
    assert page_size(250, {"maxRecordCount": 1000}) == 250


def test_server_max():
    assert page_size(None, {"maxRecordCount": 500}) == 500


def test_server_max_capped():
    assert page_size(None, {"maxRecordCount": 100_000}) == 2000


def test_default_when_server_silent():
    assert page_size(None, {}) == 1000
