import datetime as dt

from cadastre_gnaf.report import kaggle_readme_markdown

FILES = [{"file": "NSW_parcels.parquet", "state": "NSW", "kind": "parcels", "rows": 3000, "size_mb": 9.0,
          "description": "NSW land parcels"},
         {"file": "ACT_parcels.parquet", "state": "ACT", "kind": "parcels", "rows": 100, "size_mb": 1.0,
          "description": "ACT land parcels"},
         {"file": "summary.csv", "state": None, "kind": "summary", "rows": 8, "size_mb": 0.002,
          "description": "Summary"}]
SUMMARY = [{"state": "ACT", "parcels_written": 100.0, "parcels_matching_gnaf_key": 80.0, "gnaf_addresses": 60.0,
            "address_link_rate": 0.9},
           {"state": "WA", "parcels_written": 10.0, "parcels_matching_gnaf_key": 0.0, "gnaf_addresses": None,
            "address_link_rate": None},
           {"state": "SA", "parcels_written": None}]
ATTRIBUTION = "# Data sources and licences\n\n- **ACT**: (c) ACT. Source: http://act\n\nBuilt 2026-01-01T00:00.\n"


def readme():
    return kaggle_readme_markdown(FILES, SUMMARY, "me/au-parcels", ATTRIBUTION, built=dt.datetime(2026, 10, 30, 9, 0))


def test_files_and_totals():
    md = readme()
    assert md.startswith("# Australian Land Parcels (Cadastre) + G-NAF\n")
    assert "3,100 land parcels from the open state cadastres of NSW, ACT" in md
    assert "| `NSW_parcels.parquet` | 3,000 | 9.0 | NSW land parcels |" in md
    assert "`data_dictionary.md` / `.csv`" in md


def test_coverage_skips_states_without_parcels():
    md = readme()
    assert "| ACT | 100 | 80.0% | 60 | 90.0% |" in md
    assert "| WA | 10 |  |  |  |" in md
    assert "| SA |" not in md


def test_examples_use_kaggle_path_and_smallest_state():
    md = readme()
    assert 'DATA = "/kaggle/input/au-parcels"' in md
    assert 'pd.read_parquet(f"{DATA}/ACT_parcels.parquet", columns=cols)' in md
    assert "geopandas" in md and "links" not in md


def test_attribution_lines_only():
    md = readme()
    assert "## Licences and attribution\n\n- **ACT**: (c) ACT. Source: http://act\n" in md
    assert "2026-01-01" not in md
    assert md.endswith("Built 2026-10-30T09:00.\n")


def test_no_summary_or_attribution():
    md = kaggle_readme_markdown(FILES, [], "me/x")
    assert "## Coverage" not in md and "## Licences" not in md


def test_gnaf_join_example():
    md = readme()
    assert 'f"{GNAF}/ACT_ADDRESS_DETAIL_psv.psv"' in md
    assert 'explode("gnaf_address_detail_pids")' in md


def test_csv_example():
    md = readme()
    assert 'pd.read_csv(f"{DATA}/ACT_parcels.csv"' in md and '.str.split("|")' in md
