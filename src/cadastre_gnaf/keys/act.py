from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key


def keys_act(a):
    dist, div = attr_value(a, "DISTRICT_SHORT"), attr_value(a, "DIVISION_SHORT")
    sec, blk = attr_value(a, "SECTION_NUMBER"), attr_value(a, "BLOCK_NUMBER")
    return {
        "key_dist_div_sec_blk": join_key(dist, div, sec, blk, required=[0, 3]),  # CANB/BRAD/18/41
        "key_dist_blk": join_key(dist, blk),                                      # JERV/927 style
    }
