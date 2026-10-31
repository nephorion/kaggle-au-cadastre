from pathlib import Path

from cadastre_gnaf.gnaf import GnafSource


def test_defaults_to_neither():
    assert GnafSource() == GnafSource(zip=None, root=None)


def test_folder_source():
    assert GnafSource(root=Path("g")).root == Path("g")
