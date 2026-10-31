from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key
from cadastre_gnaf.keys.norm_key import norm_key


def keys_nsw(a):
    lot, sec = attr_value(a, "lotnumber"), attr_value(a, "sectionnumber")
    num, label = attr_value(a, "plannumber"), attr_value(a, "planlabel")
    doc = join_key(lot, sec, num) if sec else join_key(lot, num)    # documented: 13/31993, 11/C/3625
    return {
        "key_lot_sec_plannum": doc,
        "key_lotidstring": norm_key(attr_value(a, "lotidstring")),    # e.g. 1//DP12345
        "key_lot_sec_label": join_key(lot, sec, label, required=[0, 2]),
        "key_lot_label": join_key(lot, label),
    }
