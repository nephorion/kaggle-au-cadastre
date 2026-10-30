import pytest

from cadastre_gnaf.gnaf import GnafSource, open_table


def test_reads_from_zip(gnaf):
    with open_table(gnaf, "ACT", "ADDRESS_DETAIL") as fh:
        assert fh.readline().startswith(b"ADDRESS_DETAIL_PID|")


def test_table_name_is_case_insensitive_in_zip(gnaf):
    with open_table(gnaf, "act", "address_detail") as fh:
        assert fh.readline()


def test_reads_from_folder(gnaf_dir):
    with open_table(GnafSource(root=gnaf_dir), "ACT", "ADDRESS_DEFAULT_GEOCODE") as fh:
        assert b"LONGITUDE" in fh.readline()


def test_missing_table(gnaf, gnaf_dir):
    with pytest.raises(FileNotFoundError):
        open_table(gnaf, "NSW", "ADDRESS_DETAIL")
    with pytest.raises(FileNotFoundError):
        open_table(GnafSource(root=gnaf_dir), "NSW", "ADDRESS_DETAIL")
