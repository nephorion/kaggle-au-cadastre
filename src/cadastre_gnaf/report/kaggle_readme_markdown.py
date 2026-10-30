import datetime as dt

TITLE = "Australian Land Parcels (Cadastre) + G-NAF"
SUBTITLE = "State cadastre parcels with geometry, linked to G-NAF addresses"


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
           "one CSV per state, each parcel keyed to **G-NAF** (Geoscape's Geocoded National Address File) "
           "through its `LEGAL_PARCEL_ID`, plus an address-to-parcel link table per state and a parcels file "
           "with the addresses already joined in.", "",
           "Each parcel row has:", "",
           "- the parcel's attributes as published by the state",
           "- `gnaf_legal_parcel_id`, `gnaf_key_matched` and `gnaf_address_count`",
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

    out += ["## Using the data on Kaggle", "",
            "Add this dataset to a notebook (**Add Input**), then:", "",
            "### Load parcels without geometry (fast)", "",
            "The `wkt` column holds most of each file's size. Skip it unless you need the polygons:", "",
            "```python",
            "import pandas as pd",
            "",
            f'DATA = "/kaggle/input/{slug}"',
            "",
            'cols = ["state", "source_oid", "gnaf_legal_parcel_id", "gnaf_key_matched",',
            '        "gnaf_address_count", "point_lon", "point_lat"]',
            f'parcels = pd.read_csv(f"{{DATA}}/{ex}_parcels.csv", usecols=cols)',
            "parcels.head()",
            "```", "",
            "### Parcels with their addresses (no join needed)", "",
            "`<STATE>_parcels_with_addresses.csv` has one row per parcel and address: a parcel with three "
            "addresses appears three times, and a parcel without an address appears once with empty "
            "`address_*` columns.", "",
            "```python",
            'pa = pd.read_csv(f"{DATA}/' + ex + '_parcels_with_addresses.csv",',
            '                 usecols=lambda c: c != "wkt", dtype={"address_postcode": str})',
            'pa[["source_oid", "gnaf_legal_parcel_id", "address_full", "address_lon", "address_lat"]].head()',
            "",
            "unaddressed = pa[pa[\"address_detail_pid\"].isna()]",
            "```", "",
            "### Addresses per parcel (from the link table)", "",
            "```python",
            f'links = pd.read_csv(f"{{DATA}}/{ex}_gnaf_address_parcel_links.csv")',
            'print(links["method"].value_counts())',
            "",
            'per_parcel = links.groupby("source_oid")["address_detail_pid"].nunique()',
            'parcels["addresses"] = parcels["source_oid"].map(per_parcel).fillna(0).astype(int)',
            'parcels["addresses"].clip(upper=10).value_counts().sort_index().plot.bar(',
            '    title="Addresses per parcel (10 = 10 or more)")',
            "```", "",
            "`address_detail_pid` joins to `ADDRESS_DETAIL_PID` in G-NAF (attach a G-NAF dataset or download it "
            "from data.gov.au) to get street addresses and geocodes.", "",
            "### Polygons with GeoPandas", "",
            "```python",
            "import geopandas as gpd",
            "",
            f'df = pd.read_csv(f"{{DATA}}/{ex}_parcels.csv", usecols=["source_oid", "gnaf_legal_parcel_id", "wkt"])',
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
            "### Large states in chunks", "",
            "NSW and VIC have several million rows each. Read them in chunks if memory is tight:", "",
            "```python",
            "matched = 0",
            'for chunk in pd.read_csv(f"{DATA}/NSW_parcels.csv", usecols=["gnaf_key_matched"], chunksize=500_000):',
            '    matched += chunk["gnaf_key_matched"].sum()',
            "```", "",
            "## How it was built", "",
            "Parcels were paged out of each state's public ArcGIS REST service by ObjectID. Esri polygons were "
            "converted to WKT and given an interior point. For each state several candidate keys in G-NAF's "
            "`LEGAL_PARCEL_ID` format were built from the parcel attributes; each parcel uses the first candidate "
            "that exists in G-NAF (match rates per candidate are in `summary.csv`). Addresses were then linked to "
            "parcels by that key, with a point-in-polygon join for WA.", "",
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
