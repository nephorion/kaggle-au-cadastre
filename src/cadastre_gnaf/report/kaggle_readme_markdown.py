import datetime as dt

from cadastre_gnaf.constants import HARMONISED_COLUMNS, LEADING_COLUMNS
from cadastre_gnaf.publish.mapping_markdown import mapping_markdown
from cadastre_gnaf.report.descriptions import HARMONISED_COLUMNS as HARMONISED
from cadastre_gnaf.report.descriptions import PARCEL_COLUMNS

TITLE = "Australian Land Parcels (Cadastre) + G-NAF"
SUBTITLE = "State cadastre parcels with geometry, keyed to G-NAF addresses"
GNAF_DATA_GOV_URL = "https://data.gov.au/data/dataset/geocoded-national-address-file-g-naf"


def _num(v):
    return "" if v is None else f"{int(v):,}"


def _pct(n, d):
    return "" if not n or not d else f"{n / d:.1%}"


def _creation_markdown(gnaf_kaggle_id, gnaf_url, built):
    """The "How this dataset was created" section: the build pipeline, step by step."""
    return [
        "## How this dataset was created", "",
        f"The dataset was built on {built:%d %B %Y} by the open-source `cadastre-gnaf` pipeline, in five steps. "
        "Every step is automatic, and the same commands rebuild the dataset from a fresh snapshot.", "",
        "```",
        "state ArcGIS services ──► 1. download ──► 2. candidate keys ──► 3. link G-NAF ◄── G-NAF release",
        "                                                                     │",
        "                          5. docs ◄── parquet/ + csv/ ◄── 4. harmonise & publish",
        "```", "",
        "**1. Download the state cadastres.** Every parcel was downloaded from each state's public ArcGIS REST "
        "service (listed under [Licences and attribution](#licences-and-attribution)), in pages of ObjectID "
        "ranges. Every attribute the state publishes was kept. Esri polygons were converted to WKT in "
        "EPSG:4326 (6 decimals, about 0.1 m), with a point guaranteed to lie inside each parcel "
        "(`point_lon`, `point_lat`). `summary.csv` compares the rows downloaded with the feature count each "
        "service reported.", "",
        "**2. Build candidate G-NAF keys.** G-NAF identifies a parcel by `LEGAL_PARCEL_ID`, and each state "
        "writes it differently. From each parcel's attributes, several candidate keys were built in that format, "
        "for example NSW `13/31993` or `11/C/3625` and QLD `66/RP139841`.", "",
        "**3. Link G-NAF addresses.** The parcels were matched against the official G-NAF release (GDA2020, "
        f"from [data.gov.au]({GNAF_DATA_GOV_URL}))"
        + (f", the same release as [{gnaf_kaggle_id}]({gnaf_url})" if gnaf_kaggle_id else "") + ". "
        "Retired addresses were left out.", "",
        "- *Key join*: each parcel uses the first candidate key that exists in G-NAF (`gnaf_legal_parcel_id`, "
        "`gnaf_key_matched`). Every address with that key is linked to the parcel (method `legal_parcel_id`). "
        "The match rate of each candidate is in `summary.csv`.",
        "- *Geometry groups*: parcels with exactly the same polygon, such as stacked strata lots, share a "
        "`geometry_group_id`, the lowest `source_oid` in the stack.",
        "- *Spatial join*: WA's public layer has no lot/plan attributes, so WA addresses were linked by point "
        "in polygon (method `spatial_within`). Each address goes to the **smallest** polygon containing its "
        "G-NAF geocode, and to only one parcel per geometry group. Each address is therefore linked to "
        "exactly one parcel.",
        "- *Locality*: each parcel gets the most common locality of its linked addresses.", "",
        "**4. Harmonise and publish.** Each state's attributes were mapped onto the shared "
        "[harmonised columns](#2-harmonised-columns), such as lot, plan, tenure, status and stated area; the "
        "mapping table below shows the rule for every column and state. Area and perimeter were computed in "
        "Australian Albers equal-area (EPSG:3577), after repairing invalid polygons, so they compare across "
        "states. The state's own attributes were kept as `src_*` columns, without redundant copies. Each state "
        "was then written as a typed, zstd-compressed Parquet file and a CSV with the same columns.", "",
        "**5. Document.** `summary.csv`, `ATTRIBUTION.md`, this README, the data dictionary (from the Parquet "
        "schemas, sample values and the states' own field descriptions) and the Kaggle metadata were generated "
        "from the published files.", "",
        "**Checks.** Row counts in the published files match the download counts in `summary.csv`. The CSV and "
        "Parquet files have identical columns, and every state's file has the same layout.", ""]


def kaggle_readme_markdown(files, summary, kaggle_id, attribution="", built=None,
                           gnaf_kaggle_id=None):
    """README.md for the Kaggle dataset: contents, coverage, usage examples and licences.

    `files` comes from dataset_files, `summary` is the rows of summary.csv (dicts) and `attribution`
    the ATTRIBUTION.md text, whose "- " source lines are copied in. `gnaf_kaggle_id` is the flat G-NAF
    dataset (one CSV row per address, under `gnaf_csv/`) used in the join example; without it the
    example uses a placeholder input name.
    """
    built = built or dt.datetime.now()
    slug = kaggle_id.split("/")[-1]
    gnaf_slug = gnaf_kaggle_id.split("/")[-1] if gnaf_kaggle_id else "<flat-gnaf-dataset>"
    gnaf_url = f"https://www.kaggle.com/datasets/{gnaf_kaggle_id}" if gnaf_kaggle_id else None
    gnaf_ref = (f"the same G-NAF release as [{gnaf_kaggle_id}]({gnaf_url}), a flat copy of G-NAF"
                if gnaf_kaggle_id else "a flat copy of G-NAF")
    parcels = [f for f in files if f["kind"] == "parcels"]
    states = [f["state"] for f in parcels]
    ex = "ACT" if "ACT" in states else min(parcels, key=lambda f: f["size_mb"])["state"] if parcels else "ACT"
    total = sum(f["rows"] for f in parcels)

    out = [f"# {TITLE}", "", f"*{SUBTITLE}.*", "",
           f"{total:,} land parcels from the open state cadastres of {', '.join(states) or 'Australia'}, "
           "one file per state in `parquet/` and the same in `csv/`. Every parcel carries the ids of its **G-NAF** "
           "addresses "
           "(Geoscape's Geocoded National Address File), so it joins straight to any copy of G-NAF with no "
           "link table.", "",
           "Each state is in its own files, and every file has the same layout. Each parcel row has:", "",
           "- harmonised columns that mean the same in every state: lot, section, plan, tenure, status, "
           "area, locality and more",
           "- the parcel's attributes as published by the state (`src_*`)",
           "- `gnaf_legal_parcel_id`: the parcel key in G-NAF `LEGAL_PARCEL_ID` format, and `gnaf_key_matched`",
           "- `gnaf_address_detail_pids`: list of G-NAF `ADDRESS_DETAIL_PID`s on the parcel (null if none), "
           "with `gnaf_address_count` and `gnaf_link_methods`",
           "- `point_lon` / `point_lat`: a point guaranteed to lie inside the parcel",
           "- `wkt`: the boundary polygon (EPSG:4326)", "",
           "**Contents:** [Files](#files) · [Coverage](#coverage) · "
           "[How this dataset was created](#how-this-dataset-was-created) · [Columns](#columns) · "
           "[Using the data on Kaggle](#using-the-data-on-kaggle) · [Caveats](#caveats) · "
           "[Licences and attribution](#licences-and-attribution)", "",
           "## Files", "",
           "| File | Rows | Size (MB) | Contents |", "|---|---:|---:|---|"]
    out += [f"| `{f['file']}` | {f['rows']:,} | {f['size_mb']:,} | {f['description']} |" for f in files]
    out += ["| `data_dictionary.md` / `.csv` | | | Every column of every file: type, description, example |",
            "| `ATTRIBUTION.md` | | | Sources and licences |", ""]

    rows = [s for s in summary if s.get("parcels_written")]
    if rows:
        out += ["## Coverage", "",
                "| State | Parcels | Parcels with a G-NAF key match | G-NAF addresses | Addresses linked |",
                "|---|---:|---:|---:|---:|"]
        out += [f"| {s['state']} | {_num(s['parcels_written'])} | "
                f"{_pct(s.get('parcels_matching_gnaf_key'), s['parcels_written'])} | "
                f"{_num(s.get('gnaf_addresses'))} | "
                + (f"{s['address_link_rate']:.1%}" if s.get("address_link_rate") is not None else "") + " |"
                for s in rows]
        out += ["", "Strata buildings, roads and unaddressed land explain most parcels without an address. "
                "WA's public layer has geometry only, so WA addresses are linked spatially (address point inside "
                "the parcel polygon) instead of by key.", ""]

    out += _creation_markdown(gnaf_kaggle_id, gnaf_url, built)
    out += ["## Columns", "",
            "Every parcels file, for every state and in both formats, has the same layout:", "",
            "1. **Identity, G-NAF and geometry-group columns** (the same in every state)",
            "2. **Harmonised columns** (the same in every state; null where a state does not publish the "
            "information)",
            "3. **`src_*` columns**: the state's own attributes as published, renamed to lower-case snake case "
            "(`TENURE_TY` → `src_tenure_ty`). These differ between states.",
            "4. **`wkt`**: the polygon", "",
            "### 1. Identity, G-NAF and geometry groups", "",
            "| Column | Type | Description |", "|---|---|---|"]
    out += [f"| `{c}` | {PARCEL_COLUMNS[c][0]} | {PARCEL_COLUMNS[c][1]} |" for c in LEADING_COLUMNS]
    out += ["", "### 2. Harmonised columns", "",
            "| Column | Type | Description |", "|---|---|---|"]
    out += [f"| `{c}` | {HARMONISED[c][0]} | {HARMONISED[c][1]} |" for c in HARMONISED_COLUMNS]
    out += ["", "Where each harmonised column comes from, per state (`polygon` = computed from the geometry; "
            "– = not available, always null):", "", mapping_markdown(), "",
            "### 3. Source columns", "",
            "Every `src_*` column of every file, with the state's own description where it publishes one, is "
            "in `data_dictionary.md` / `data_dictionary.csv`. The states' ObjectID copies and service-computed "
            "`Shape__Area` / `Shape__Length` fields are left out (see `source_oid`, `area_m2`, `perimeter_m`).", "",
            "## Using the data on Kaggle", "",
            "Add this dataset to a notebook (**Add Input**), then:", "",
            "### Load parcels without geometry (fast)", "",
            "Parquet reads only the columns you ask for. Leave out `wkt` unless you need the polygons:", "",
            "```python",
            "import pandas as pd",
            "",
            f'DATA = "/kaggle/input/{slug}"',
            "",
            'cols = ["state", "source_oid", "gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count",',
            '        "gnaf_address_detail_pids", "point_lon", "point_lat"]',
            f'parcels = pd.read_parquet(f"{{DATA}}/parquet/{ex}_parcels.parquet", columns=cols)',
            "parcels.head()",
            "```", "",
            "### All states in one table", "",
            "The identity, G-NAF and harmonised columns are the same in every file, so states stack directly:", "",
            "```python",
            "import glob",
            "",
            'common = ["state", "source_oid", "gnaf_legal_parcel_id", "gnaf_address_count", "lot", "plan",',
            '          "parcel_label", "status", "tenure", "is_strata", "area_m2", "locality"]',
            'files = sorted(glob.glob(f"{DATA}/parquet/*_parcels.parquet"))',
            "australia = pd.concat([pd.read_parquet(f, columns=common) for f in files], ignore_index=True)",
            "",
            "# median parcel size (m²) by state and tenure, leaving out retired and proposed parcels",
            'live = australia[~australia["status"].isin(["retired", "proposed"])]',
            'live.groupby(["state", "tenure"], dropna=False)["area_m2"].median().unstack()',
            "```", "",
            "Harmonised columns are null where a state does not publish the information, so check the mapping "
            "table above before comparing states (for example, only QLD, TAS and ACT have `tenure` for every "
            "parcel).", "",
            "### Join G-NAF addresses", "",
            f"Join the addresses from {gnaf_ref} with one row per address (full address, locality, postcode, "
            "geocode and more). Add it "
            "to the notebook as a second input. `gnaf_address_detail_pids` is a list per parcel: explode it to "
            "one row per address and merge:", "",
            "```python",
            "import glob",
            "",
            f'GNAF = "/kaggle/input/{gnaf_slug}/gnaf_csv"      # files gnaf_<STATE>_<postcode area>.csv',
            'gnaf_cols = ["address_detail_pid", "full_address", "locality_name", "postcode_effective",',
            '             "longitude", "latitude"]',
            "gnaf = pd.concat([pd.read_csv(f, usecols=gnaf_cols, dtype=str)",
            f'                  for f in glob.glob(f"{{GNAF}}/gnaf_{ex}_*.csv")], ignore_index=True)',
            "",
            'parcel_addresses = (parcels.explode("gnaf_address_detail_pids")',
            '                           .merge(gnaf, how="left", left_on="gnaf_address_detail_pids",',
            '                                  right_on="address_detail_pid"))',
            'parcel_addresses[["source_oid", "gnaf_legal_parcel_id", "full_address", "locality_name"]].head()',
            "```", "",
            "Parcels without an address keep one row with null address columns. Key-matched parcels can also be "
            "joined on `gnaf_legal_parcel_id` = G-NAF's `legal_parcel_id`. The raw G-NAF tables (PSV, as "
            "released by Geoscape) are on "
            f"[data.gov.au]({GNAF_DATA_GOV_URL}).", "",
            "### Addresses per parcel", "",
            "```python",
            'parcels["gnaf_address_count"].clip(upper=10).value_counts().sort_index().plot.bar(',
            '    title="Addresses per parcel (10 = 10 or more)")',
            "```", "",
            "### Polygons with GeoPandas", "",
            "```python",
            "import geopandas as gpd",
            "",
            f'df = pd.read_parquet(f"{{DATA}}/parquet/{ex}_parcels.parquet",',
            '                     columns=["source_oid", "gnaf_legal_parcel_id", "wkt"])',
            'gdf = gpd.GeoDataFrame(df.drop(columns="wkt"), geometry=gpd.GeoSeries.from_wkt(df["wkt"]), crs=4326)',
            "",
            'gdf["area_m2"] = gdf.to_crs(3577).area      # Australian Albers equal-area',
            "gdf.plot(figsize=(10, 10), linewidth=0)",
            "```", "",
            "### Find the parcel under a point", "",
            "```python",
            "from shapely.geometry import Point",
            "",
            'pt = Point(parcels.loc[0, "point_lon"], parcels.loc[0, "point_lat"])   # any lon/lat',
            "gdf[gdf.contains(pt)]",
            "```", "",
            "### CSV instead of Parquet", "",
            "Every file in `parquet/` has a twin in `csv/` with the same columns. Lists are `|`-separated text "
            "there:", "",
            "```python",
            f'csv = pd.read_csv(f"{{DATA}}/csv/{ex}_parcels.csv", usecols=cols, dtype={{"gnaf_legal_parcel_id": str}})',
            'csv["gnaf_address_detail_pids"] = csv["gnaf_address_detail_pids"].str.split("|")',
            "```", "",
            "### Stacked parcels (identical polygons)", "",
            "Some parcels share exactly the same polygon, typically strata lots drawn with the building's "
            "footprint (common in WA). They have the same `geometry_group_id`; `geometry_group_size` says how "
            "many share it. Addresses linked spatially go to one parcel per stack, the one whose `source_oid` "
            "equals `geometry_group_id`.", "",
            "```python",
            'p = pd.read_parquet(f"{DATA}/parquet/WA_parcels.parquet",',
            '                    columns=["source_oid", "geometry_group_id", "geometry_group_size",',
            '                             "gnaf_address_count"])',
            "",
            "# one row per distinct polygon (for maps, areas, counting land parcels)",
            'footprints = p[p["source_oid"] == p["geometry_group_id"]]',
            "",
            "# every lot in the same stack as a given parcel",
            'stack = p[p["geometry_group_id"] == p.loc[0, "geometry_group_id"]]',
            "",
            "# how much stacking there is",
            'p["geometry_group_size"].clip(upper=10).value_counts().sort_index()',
            "```", "",
            "### Large states", "",
            "NSW and VIC have several million rows each. Select columns and filter rows while reading:", "",
            "```python",
            'nsw = pd.read_parquet(f"{DATA}/parquet/NSW_parcels.parquet",',
            '                      columns=["source_oid", "gnaf_legal_parcel_id", "gnaf_address_detail_pids"],',
            '                      filters=[("gnaf_address_count", ">", 0)])',
            "```", "",
            "## Caveats", "",
            "- SA and NT cadastres are not open data and are not included.",
            "- Cadastral polygons are graphical representations only, not legal boundaries.",
            "- Source columns differ between states; see `data_dictionary.md`.",
            "- Each state is a snapshot taken on the build date below.", ""]
    credits = [line for line in attribution.splitlines() if line.startswith("- ")]
    if credits:
        out += ["## Licences and attribution", "", *credits, ""]
    out.append(f"Built {built.isoformat(timespec='minutes')}.")
    return "\n".join(out) + "\n"
