import datetime as dt

from cadastre_gnaf.report import attribution_markdown


def test_lists_sources_gnaf_and_build_time():
    rows = [{"state": "NSW", "licence": "CC BY", "source": "http://nsw"}]
    md = attribution_markdown(rows, built=dt.datetime(2026, 10, 30, 9, 15, 42))
    assert md.startswith("# Data sources and licences\n\n- **NSW**: CC BY. Source: http://nsw\n")
    assert "**G-NAF**" in md
    assert "not legal boundaries" in md
    assert md.endswith("Built 2026-10-30T09:15.\n")
