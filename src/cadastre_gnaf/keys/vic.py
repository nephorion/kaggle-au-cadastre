from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.norm_key import norm_key


def keys_vic(a):
    return {"key_spi": norm_key(attr_value(a, "parcel_spi"))}       # e.g. 1TP201500
