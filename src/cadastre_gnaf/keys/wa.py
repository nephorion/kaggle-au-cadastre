from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key


def keys_wa(a):
    # Only usable if you point WA at a SLIP subscription layer that has these fields.
    pi, lot = attr_value(a, "pi_parcel", "piparcel"), attr_value(a, "lot_number", "lotnumber")
    return {"key_piparcel_lot": join_key(pi, lot)}                   # e.g. S030337/1
