from cadastre_gnaf.arcgis import layer_info
from cadastre_gnaf.storage import read_progress


def source_fields(config, session, state, source):
    """{name: ArcGIS field dict} for a state's source layer.

    Uses the field list saved at download time; otherwise asks the service (if `session` is given).
    Returns {} when neither is available, so the dictionary still builds offline.
    """
    fields = read_progress(config, state).get("fields")
    if fields is None and session is not None and source.url:
        try:
            info, _ = layer_info(session, source.url, config.arcgis_tokens.get(state))
            fields = info.get("fields", [])
        except Exception as e:
            print(f"[{state}] could not read field metadata: {e!r}")
    return {f["name"]: f for f in fields or []}
