"""Run configuration, built from the command line (or directly in code/tests)."""

from dataclasses import dataclass, field
from pathlib import Path

from cadastre_gnaf.constants import DEFAULT_STATES


@dataclass(frozen=True)
class Config:
    states: tuple[str, ...] = DEFAULT_STATES
    step: str = "all"                                   # "all" | "download" | "gnaf"
    out_dir: Path = Path("./cadastre_out")
    work_dir: Path = Path("./cadastre_work")
    compress: bool = False
    include_wkt: bool = True
    decimals: int = 6
    workers: int = 4
    page_size: int | None = None
    force: bool = False
    gnaf_dir: Path | None = None
    gnaf_zip_url: str | None = None
    spatial_join_states: tuple[str, ...] = ("WA",)
    local_sources: dict[str, str] = field(default_factory=dict)
    arcgis_tokens: dict[str, str] = field(default_factory=dict)   # e.g. {"WA": "<SLIP token>"}

    @property
    def csv_ext(self) -> str:
        return ".csv.gz" if self.compress else ".csv"

    @property
    def compression(self) -> str | None:
        return "gzip" if self.compress else None

    @property
    def progress_dir(self) -> Path:
        return self.out_dir / "_progress"

    @property
    def do_download(self) -> bool:
        return self.step in ("all", "download")

    @property
    def do_gnaf(self) -> bool:
        return self.step in ("all", "gnaf")
