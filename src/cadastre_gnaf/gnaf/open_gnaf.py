import zipfile
from pathlib import Path

from cadastre_gnaf.gnaf.download_file import download_file
from cadastre_gnaf.gnaf.gnaf_source import GnafSource
from cadastre_gnaf.gnaf.latest_gnaf_zip_url import latest_gnaf_zip_url


def open_gnaf(config, session):
    """Use --gnaf-dir if given, else download the G-NAF zip into the work folder."""
    if config.gnaf_dir:
        return GnafSource(root=Path(config.gnaf_dir))
    z = config.work_dir / "gnaf.zip"
    download_file(session, config.gnaf_zip_url or latest_gnaf_zip_url(session), z)
    return GnafSource(zip=zipfile.ZipFile(z))
