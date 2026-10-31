from cadastre_gnaf.keys import keys_vic


def test_spi():
    assert keys_vic({"parcel_spi": "1\\TP201500"}) == {"key_spi": "1\\TP201500"}
    assert keys_vic({"PARCEL_SPI": " 1tp201500 "}) == {"key_spi": "1TP201500"}


def test_missing():
    assert keys_vic({}) == {"key_spi": None}
