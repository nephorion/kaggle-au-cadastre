MAX_PAGE_SIZE = 2000


def page_size(requested, layer_info):
    """Features per request: the requested size, else the server max (capped at 2000)."""
    if requested:
        return int(requested)
    return min(int(layer_info.get("maxRecordCount") or 1000), MAX_PAGE_SIZE)
