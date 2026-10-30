import pandas as pd

from cadastre_gnaf.gnaf import read_address_parcels, read_address_points
from cadastre_gnaf.keys import key_names
from cadastre_gnaf.linking.choose_keys import choose_keys
from cadastre_gnaf.linking.fallback_keys import fallback_keys
from cadastre_gnaf.linking.key_links import key_links
from cadastre_gnaf.linking.read_parcel_keys import read_parcel_keys
from cadastre_gnaf.linking.rewrite_parcels import rewrite_parcels
from cadastre_gnaf.linking.score_keys import score_keys
from cadastre_gnaf.linking.spatial_fallback_links import spatial_fallback_links
from cadastre_gnaf.storage import links_path, parcels_path


def finalise_state(config, gnaf, state, source):
    """Pick the G-NAF key, write the address links and add G-NAF columns to the parcels CSV.

    `gnaf` may be None, in which case only the best available key is filled in.
    Returns a summary dict, or None if the state has no parcels CSV.
    """
    path = parcels_path(config, state)
    if not path.exists():
        return None
    knames = key_names(source.keys)
    kd = read_parcel_keys(path, knames)
    summ = {"state": state, "parcels": len(kd)}

    if gnaf is not None:
        g = read_address_parcels(gnaf, state)
        gset = set(g["key"].dropna())
        stats = score_keys(kd, gset)
        summ["key_match"] = {k: f"{n:,}/{t:,}" for k, n, t in stats}
        print(f"[{state}] parcels matching G-NAF LEGAL_PARCEL_ID by candidate:", summ["key_match"])
        chosen, matched = choose_keys(kd, [s[0] for s in stats], gset)
        links = key_links(g, chosen, matched)
        if state in config.spatial_join_states and config.include_wkt:
            extra = spatial_fallback_links(path, g, read_address_points(gnaf, state),
                                           links["address_detail_pid"], label=state)
            links = pd.concat([links, extra], ignore_index=True)
        links["source_oid"] = links["source_oid"].astype(str)
        links.to_csv(links_path(config, state), index=False, compression=config.compression)
        counts = links.groupby("source_oid")["address_detail_pid"].nunique()
        summ["gnaf_addresses"] = len(g)
        summ["addresses_linked"] = int(links["address_detail_pid"].nunique())
        summ["address_link_rate"] = round(summ["addresses_linked"] / max(1, len(g)), 4)
        summ["parcels_with_gnaf_key_match"] = int(matched.sum())
    else:
        chosen, matched = fallback_keys(kd)
        counts = pd.Series(dtype=int)

    rewrite_parcels(path, len(knames), chosen, matched, counts, config.compression)
    print(f"[{state}] finalised {path.name}: {summ}")
    return summ
