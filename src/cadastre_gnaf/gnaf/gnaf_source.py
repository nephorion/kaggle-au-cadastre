import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GnafSource:
    """A G-NAF release: either the downloaded zip or an extracted folder (exactly one is set)."""
    zip: zipfile.ZipFile | None = None
    root: Path | None = None
