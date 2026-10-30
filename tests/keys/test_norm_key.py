from cadastre_gnaf.keys import norm_key


def test_uppercases_and_removes_whitespace():
    assert norm_key(" 1 / dp 123\t") == "1/DP123"


def test_none_stays_none():
    assert norm_key(None) is None


def test_empty_after_normalising_is_none():
    assert norm_key("   ") is None


def test_non_string_input():
    assert norm_key(42) == "42"
