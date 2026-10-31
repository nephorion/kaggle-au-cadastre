from cadastre_gnaf.gnaf import read_table


def test_reads_selected_columns_and_drops_retired(gnaf):
    df = read_table(gnaf, "ACT", "ADDRESS_DETAIL", {"ADDRESS_DETAIL_PID", "DATE_RETIRED"})
    assert list(df.columns) == ["ADDRESS_DETAIL_PID"]
    assert "GAACT4" not in df["ADDRESS_DETAIL_PID"].tolist()
    assert len(df) == 4


def test_keeps_values_as_strings(gnaf):
    df = read_table(gnaf, "ACT", "ADDRESS_DEFAULT_GEOCODE", {"LONGITUDE"})
    assert df["LONGITUDE"].tolist()[:2] == ["149.5", "149.5"]
