import json

from cadastre_gnaf.storage import read_progress


def summary_rows(config, sources, summaries):
    """One row per state in `sources`: source, counts, G-NAF match rates and licence.

    G-NAF figures come from `summaries` (this run) or else from the state's saved progress (earlier runs),
    so a run limited to some states keeps the others' figures.
    """
    rows = []
    for st in sources:
        p = read_progress(config, st)
        s = next((x for x in summaries if x["state"] == st), None) or p.get("gnaf", {})
        rows.append({
            "state": st,
            "source": sources[st].url or config.local_sources.get(st, "not available (licensed)"),
            "features_expected": p.get("expected"),
            "parcels_written": s.get("parcels"),
            "parcels_matching_gnaf_key": s.get("parcels_with_gnaf_key_match"),
            "gnaf_addresses": s.get("gnaf_addresses"),
            "address_link_rate": s.get("address_link_rate"),
            "key_match_by_candidate": json.dumps(s.get("key_match")) if s.get("key_match") else None,
            "licence": sources[st].licence,
        })
    return rows
