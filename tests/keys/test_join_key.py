from cadastre_gnaf.keys import join_key


def test_joins_with_slash_and_normalises():
    assert join_key("1", "dp 12") == "1/DP12"


def test_all_parts_required_by_default():
    assert join_key("1", "") is None


def test_only_listed_parts_required():
    assert join_key("1", "", "DP12", required=[0, 2]) == "1//DP12"
    assert join_key("", "C", "DP12", required=[0, 2]) is None


def test_no_parts_required():
    assert join_key("", "", required=[]) == "/"
