from cadastre_gnaf.gnaf import open_gnaf
from cadastre_gnaf.linking.finalise_state import finalise_state
from cadastre_gnaf.sources import SOURCES


def run_gnaf(config, session, sources=SOURCES, gnaf=None):
    """Finalise every configured state against G-NAF. Returns the per-state summaries."""
    gnaf = gnaf or open_gnaf(config, session)
    summaries = []
    for st in config.states:
        try:
            s = finalise_state(config, gnaf, st, sources[st])
            if s:
                summaries.append(s)
        except Exception as e:
            print(f"[{st}] finalise FAILED: {e!r}")
    return summaries
