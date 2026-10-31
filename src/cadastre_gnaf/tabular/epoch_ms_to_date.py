import datetime as dt


def epoch_ms_to_date(v):
    """Esri date (ms since epoch, UTC) -> ISO date string; returns the input unchanged if not convertible."""
    if v in (None, ""):
        return v
    try:
        return dt.datetime.fromtimestamp(v / 1000, dt.timezone.utc).date().isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return v
