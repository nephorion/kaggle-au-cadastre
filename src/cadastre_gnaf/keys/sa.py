from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key
from cadastre_gnaf.keys.norm_key import norm_key


def keys_sa(a):
    pt, plan = attr_value(a, "PLAN_T"), attr_value(a, "PLAN")
    prt, par = attr_value(a, "PARCEL_T"), attr_value(a, "PARCEL")
    return {
        "key_plant_plan_parcelt_parcel": join_key(pt, plan, prt, par),   # D/10001/A/14
        "key_dcdbid": norm_key(attr_value(a, "DCDBID")),
    }
