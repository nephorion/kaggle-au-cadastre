import json


def write_progress(config, state, data):
    config.progress_dir.mkdir(parents=True, exist_ok=True)
    (config.progress_dir / f"{state}.json").write_text(json.dumps(data))
