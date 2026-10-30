from pathlib import Path

from cadastre_gnaf.cli.build_parser import build_parser
from cadastre_gnaf.cli.parse_state_pairs import parse_state_pairs
from cadastre_gnaf.config import Config


def parse_config(argv=None):
    """Command-line arguments -> Config."""
    parser = build_parser()
    a = parser.parse_args(argv)
    try:
        local_sources, tokens = parse_state_pairs(a.local), parse_state_pairs(a.token)
    except ValueError as e:
        parser.error(str(e))
    return Config(
        states=tuple(s.upper() for s in a.states),
        step=a.step,
        out_dir=Path(a.out),
        work_dir=Path(a.work),
        compress=a.compress,
        include_wkt=not a.no_wkt,
        decimals=a.decimals,
        workers=a.workers,
        page_size=a.page_size,
        force=a.force,
        gnaf_dir=Path(a.gnaf_dir) if a.gnaf_dir else None,
        gnaf_zip_url=a.gnaf_zip_url,
        spatial_join_states=tuple(s.upper() for s in a.spatial_join),
        local_sources=local_sources,
        arcgis_tokens=tokens,
        kaggle_id=a.kaggle_id,
    )
