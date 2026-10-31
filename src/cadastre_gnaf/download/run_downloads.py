from cadastre_gnaf.download.download_arcgis_state import download_arcgis_state
from cadastre_gnaf.download.load_local_state import load_local_state
from cadastre_gnaf.sources import SOURCES


def run_downloads(config, session, sources=SOURCES):
    """Download (or load from --local) every configured state. Returns {state: error} for failures."""
    failures = {}
    for st in config.states:
        try:
            if st in config.local_sources:
                load_local_state(config, st, sources[st], config.local_sources[st])
            elif sources[st].url:
                download_arcgis_state(config, session, st, sources[st])
            else:
                print(f"[{st}] skipped: no open service. Use --local {st}=/path/to/file (see --help).")
        except Exception as e:                       # keep going; re-run to resume
            failures[st] = repr(e)
            print(f"\n[{st}] FAILED: {e!r}  (re-run to resume)")
    print("failures:", failures or "none")
    return failures
