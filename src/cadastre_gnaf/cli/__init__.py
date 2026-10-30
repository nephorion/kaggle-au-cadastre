"""Command-line interface."""

from cadastre_gnaf.cli.build_parser import build_parser
from cadastre_gnaf.cli.main import main
from cadastre_gnaf.cli.parse_config import parse_config
from cadastre_gnaf.cli.parse_state_pairs import parse_state_pairs

__all__ = ["build_parser", "main", "parse_config", "parse_state_pairs"]
