from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key
from cadastre_gnaf.keys.strip_zeros import strip_zeros


def keys_nt(a):
    loc, par, lto = attr_value(a, "PAR_LOC"), attr_value(a, "PAR_PAR"), attr_value(a, "PAR_LTO")
    return {
        "key_loc_par_lto": join_key(loc, strip_zeros(par), lto, required=[0, 1]),   # 550/3252/
        "key_loc_lto_par": join_key(loc, lto, strip_zeros(par), required=[0, 2]),
    }
