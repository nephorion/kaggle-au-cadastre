import re


def open_table(source, state, table):
    """Binary file handle for `Standard/<STATE>_<TABLE>_psv.psv` in a G-NAF release."""
    if source.zip:
        pat = re.compile(rf"(^|/)Standard/{state}_{table}_psv\.psv$", re.I)
        name = next((n for n in source.zip.namelist() if pat.search(n)), None)
        if not name:
            raise FileNotFoundError(f"{state}_{table} not in G-NAF zip")
        return source.zip.open(name)
    hit = next(iter(source.root.rglob(f"{state}_{table}_psv.psv")), None)
    if not hit:
        raise FileNotFoundError(f"{state}_{table} not under {source.root}")
    return open(hit, "rb")
