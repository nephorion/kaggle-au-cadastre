from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key
from cadastre_gnaf.keys.strip_zeros import strip_zeros


def keys_tas(a):
    vol, fol = attr_value(a, "VOLUME"), attr_value(a, "FOLIO")
    return {
        "key_vol_folio": join_key(strip_zeros(vol), strip_zeros(fol)),   # e.g. 158882/1
        "key_vol_folio_raw": join_key(vol, fol),
    }
