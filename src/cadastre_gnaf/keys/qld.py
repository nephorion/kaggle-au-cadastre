from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key
from cadastre_gnaf.keys.norm_key import norm_key


def keys_qld(a):
    lot, plan = attr_value(a, "lot"), attr_value(a, "plan")
    return {
        "key_lot_plan": join_key(lot, plan),                         # e.g. 66/RP139841
        "key_lotplan": norm_key(attr_value(a, "lotplan")),           # e.g. 66RP139841
    }
