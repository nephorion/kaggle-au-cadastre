from cadastre_gnaf.tabular import output_columns


def test_column_order():
    assert output_columns(["key_a"], ["BLOCK", "AREA"]) == \
        ["state", "source_oid", "key_a", "point_lon", "point_lat", "BLOCK", "AREA", "wkt"]


def test_clashing_attribute_names_prefixed():
    cols = output_columns([], ["state", "wkt", "gnaf_key_matched"], include_wkt=False)
    assert cols[-3:] == ["src_state", "src_wkt", "src_gnaf_key_matched"]


def test_without_wkt():
    assert "wkt" not in output_columns([], ["A"], include_wkt=False)
