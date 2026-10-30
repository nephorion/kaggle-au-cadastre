from cadastre_gnaf.gnaf import read_address_points


def test_numeric_coordinates_and_bad_rows_dropped(gnaf):
    df = read_address_points(gnaf, "ACT")
    assert df["ADDRESS_DETAIL_PID"].tolist() == ["GAACT1", "GAACT2", "GAACT3", "GAACT5"]
    assert df["LONGITUDE"].dtype.kind == "f" and df["LATITUDE"].iloc[0] == -34.5
