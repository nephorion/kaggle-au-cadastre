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


def test_gnaf_join_example_uses_the_flat_gnaf_dataset():
    md = readme()
    assert 'GNAF = "/kaggle/input/gnaf-aug-2026-all-states-gda2020-flat/gnaf_csv"' in md
    assert 'glob.glob(f"{GNAF}/gnaf_ACT_*.csv")' in md and 'explode("gnaf_address_detail_pids")' in md
    assert "(https://www.kaggle.com/datasets/your-kaggle-username/gnaf-aug-2026-all-states-gda2020-flat)" in md


def test_gnaf_dataset_is_configurable():
    md = kaggle_readme_markdown(FILES, [], "me/x", gnaf_kaggle_id="someone/my-gnaf")
    assert '"/kaggle/input/my-gnaf/gnaf_csv"' in md and "[someone/my-gnaf](" in md


def test_csv_example():
    md = readme()
    assert 'pd.read_csv(f"{DATA}/ACT_parcels.csv"' in md and '.str.split("|")' in md


def test_shared_columns_and_stacked_parcels():
    md = readme()
    assert "## Columns" in md and "| `geometry_group_id` | integer |" in md
    assert md.index("| `state` |") < md.index("| `gnaf_address_detail_pids` |") < md.index("| `point_lat` |")
    assert 'footprints = p[p["source_oid"] == p["geometry_group_id"]]' in md


def test_harmonised_columns_documented():
    md = readme()
    assert "### 2. Harmonised columns" in md and "| `area_m2` | number |" in md
    assert "| Column | NSW | VIC | QLD | TAS | ACT | WA |" in md
    assert 'glob.glob(f"{DATA}/*_parcels.parquet")' in md
