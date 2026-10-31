import json


def read_progress(config, state):
    """Resume state for a download ({} if none)."""
    p = config.progress_dir / f"{state}.json"
    return json.loads(p.read_text()) if p.exists() else {}
