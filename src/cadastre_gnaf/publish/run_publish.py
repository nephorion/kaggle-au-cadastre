from cadastre_gnaf.publish.publish_state import publish_state
from cadastre_gnaf.sources import SOURCES


def run_publish(config, session, sources=SOURCES):
    """Publish every configured state's parcels as Parquet; a failing state does not stop the others."""
    for st in config.states:
        try:
            publish_state(config, session, st, sources[st])
        except Exception as e:
            print(f"[{st}] publish FAILED: {e!r}")
