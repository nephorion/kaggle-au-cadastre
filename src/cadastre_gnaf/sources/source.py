from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """A state cadastre layer: ArcGIS REST URL (None = not open data), key builder and licence."""
    url: str | None
    keys: Callable[[dict], dict]
    licence: str
    where: str = "1=1"
