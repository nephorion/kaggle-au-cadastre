from cadastre_gnaf.keys import keys_act


def test_district_division_section_block():
    k = keys_act({"DISTRICT_SHORT": "CANB", "DIVISION_SHORT": "BRAD", "SECTION_NUMBER": 18, "BLOCK_NUMBER": 41})
    assert k == {"key_dist_div_sec_blk": "CANB/BRAD/18/41", "key_dist_blk": "CANB/41"}


def test_rural_block_without_division_or_section():
    k = keys_act({"DISTRICT_SHORT": "JERV", "BLOCK_NUMBER": 927})
    assert k == {"key_dist_div_sec_blk": "JERV///927", "key_dist_blk": "JERV/927"}


def test_missing_block():
    assert keys_act({"DISTRICT_SHORT": "CANB"}) == {"key_dist_div_sec_blk": None, "key_dist_blk": None}
