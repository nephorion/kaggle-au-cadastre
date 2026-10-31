from cadastre_gnaf.keys import key_names, keys_nsw, keys_vic


def test_returns_builder_keys_in_order():
    assert key_names(keys_nsw) == ["key_lot_sec_plannum", "key_lotidstring", "key_lot_sec_label", "key_lot_label"]


def test_single_key_builder():
    assert key_names(keys_vic) == ["key_spi"]


def test_custom_builder():
    assert key_names(lambda a: {"b": None, "a": None}) == ["b", "a"]
