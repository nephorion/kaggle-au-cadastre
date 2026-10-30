"""G-NAF LEGAL_PARCEL_ID key builders.

Each state returns several candidate keys; the G-NAF step measures which ones
actually match and uses the first matching one per parcel.
"""

from cadastre_gnaf.keys.act import keys_act
from cadastre_gnaf.keys.attr_value import attr_value
from cadastre_gnaf.keys.join_key import join_key
from cadastre_gnaf.keys.key_names import key_names
from cadastre_gnaf.keys.norm_key import norm_key
from cadastre_gnaf.keys.nsw import keys_nsw
from cadastre_gnaf.keys.nt import keys_nt
from cadastre_gnaf.keys.qld import keys_qld
from cadastre_gnaf.keys.sa import keys_sa
from cadastre_gnaf.keys.strip_zeros import strip_zeros
from cadastre_gnaf.keys.tas import keys_tas
from cadastre_gnaf.keys.vic import keys_vic
from cadastre_gnaf.keys.wa import keys_wa

__all__ = [
    "attr_value", "join_key", "key_names", "norm_key", "strip_zeros",
    "keys_act", "keys_nsw", "keys_nt", "keys_qld", "keys_sa", "keys_tas", "keys_vic", "keys_wa",
]
