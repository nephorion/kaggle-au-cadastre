import datetime as dt

from cadastre_gnaf.constants import HARMONISED_COLUMNS, LEADING_COLUMNS
from cadastre_gnaf.publish.mapping_markdown import mapping_markdown
from cadastre_gnaf.report.descriptions import HARMONISED_COLUMNS as HARMONISED
from cadastre_gnaf.report.descriptions import PARCEL_COLUMNS

TITLE = "Australian Land Parcels (Cadastre) + G-NAF"
SUBTITLE = "State cadastre parcels with geometry, keyed to G-NAF addresses"


def _num(v):
    return "" if v is None else f"{int(v):,}"


def _pct(n, d):
    return "" if not n or not d else f"{n / d:.1%}"


def kaggle_readme_markdown(files, summary, kaggle_id, attribution="", built=None):
    """README.md for the Kaggle dataset: contents, coverage, usage examples and licences.

    `files` comes from dataset_files, `summary` is the rows of summary.csv (dicts) and `attribution`
    the ATTRIBUTION.md text, whose "- " source lines are copied in.
    """
    built = built or dt.datetime.now()
    slug = kaggle_id.split("/")[-1]
    parcels = [f for f in files if f["kind"] == "parcels"]
    states = [f["state"] for f in parcels]
    ex = "ACT" if "ACT" in states else min(parcels, key=lambda f: f["size_mb"])["state"] if parcels else "ACT"
    total = sum(f["rows"] for f in parcels)

    out = [f"# {TITLE}", "", f"*{SUBTITLE}.*", "",
           f"{total:,} land parcels from the open state cadastres of {', '.join(states) or 'Australia'}, "
           "one Parquet and one CSV file per state. Every parcel carries the ids of its **G-NAF** addresses "
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
            f'parcels = pd.read_parquet(f"{{DATA}}/{ex}_parcels.parquet", columns=cols)',
            "parcels.head()",
            "```", "",
            "### All states in one table", "",
            "The identity, G-NAF and harmonised columns are the same in every file, so states stack directly:", "",
            "```python",
            "import glob",
            "",
            'common = ["state", "source_oid", "gnaf_legal_parcel_id", "gnaf_address_count", "lot", "plan",',
            '          "parcel_label", "status", "tenure", "is_strata", "area_m2", "locality"]',
            "australia = pd.concat([pd.read_parquet(f, columns=common)",
            '                       for f in sorted(glob.glob(f"{DATA}/*_parcels.parquet"))], ignore_index=True)',
            "",
            "# median parcel size (m²) by state and tenure, leaving out retired and proposed parcels",
            'live = australia[~australia["status"].isin(["retired", "proposed"])]',
            'live.groupby(["state", "tenure"], dropna=False)["area_m2"].median().unstack()',
            "```", "",
            "Harmonised columns are null where a state does not publish the information, so check the mapping "
            "table above before comparing states (for example, only QLD, TAS and ACT have `tenure` for every "
            "parcel).", "",
            "### Join G-NAF addresses", "",
            "`gnaf_address_detail_pids` is a list per parcel. Explode it to one row per address and join "
            "`ADDRESS_DETAIL` from G-NAF (attach a G-NAF dataset, or use the release from data.gov.au):", "",
            "```python",
            'GNAF = "/kaggle/input/<your-gnaf-dataset>"     # folder holding the G-NAF PSV files',
            f'detail = pd.read_csv(f"{{GNAF}}/{ex}_ADDRESS_DETAIL_psv.psv", sep="|", dtype=str)',
            "",
            "addresses = (parcels.explode(\"gnaf_address_detail_pids\")",
            "                    .merge(detail, how=\"left\", left_on=\"gnaf_address_detail_pids\",",
            "                           right_on=\"ADDRESS_DETAIL_PID\"))",
            "```", "",
            "Parcels without an address keep one row with null G-NAF columns. Key-matched parcels can also be "
            "joined on `gnaf_legal_parcel_id` = `LEGAL_PARCEL_ID` (trim spaces from G-NAF's values first).", "",
            "### Addresses per parcel", "",
            "```python",
            'parcels["gnaf_address_count"].clip(upper=10).value_counts().sort_index().plot.bar(',
            '    title="Addresses per parcel (10 = 10 or more)")',
            "```", "",
            "### Polygons with GeoPandas", "",
            "```python",
            "import geopandas as gpd",
            "",
            f'df = pd.read_parquet(f"{{DATA}}/{ex}_parcels.parquet",',
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
            "Every `.parquet` file has a `.csv` twin with the same columns. Lists are `|`-separated text there:", "",
            "```python",
            f'csv = pd.read_csv(f"{{DATA}}/{ex}_parcels.csv", usecols=cols, dtype={{"gnaf_legal_parcel_id": str}})',
            'csv["gnaf_address_detail_pids"] = csv["gnaf_address_detail_pids"].str.split("|")',
            "```", "",
            "### Stacked parcels (identical polygons)", "",
            "Some parcels share exactly the same polygon, typically strata lots drawn with the building's "
            "footprint (common in WA). They have the same `geometry_group_id`; `geometry_group_size` says how "
            "many share it. Addresses linked spatially go to one parcel per stack, the one whose `source_oid` "
            "equals `geometry_group_id`.", "",
            "```python",
            'p = pd.read_parquet(f"{DATA}/WA_parcels.parquet",',
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
            'nsw = pd.read_parquet(f"{DATA}/NSW_parcels.parquet",',
            '                      columns=["source_oid", "gnaf_legal_parcel_id", "gnaf_address_detail_pids"],',
            '                      filters=[("gnaf_address_count", ">", 0)])',
            "```", "",
            "## How it was built", "",
            "Parcels were paged out of each state's public ArcGIS REST service by ObjectID. Esri polygons were "
            "converted to WKT and given an interior point. For each state several candidate keys in G-NAF's "
            "`LEGAL_PARCEL_ID` format were built from the parcel attributes; each parcel uses the first candidate "
            "that exists in G-NAF (match rates per candidate are in `summary.csv`). Addresses were then linked to "
            "parcels by that key. WA's public layer has no lot/plan attributes, so WA addresses were linked with a "
            "point-in-polygon join instead: each address goes to the smallest polygon containing its G-NAF "
            "geocode, and to one parcel per stack of identical polygons.", "",
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
