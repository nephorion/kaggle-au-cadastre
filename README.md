# cadastre-gnaf

Download Australian state **cadastres** (land parcels) from public ArcGIS REST services and publish
**one Parquet and one CSV file per state**. Each parcel carries the ids of its **G-NAF** (Geocoded National
Address File) addresses, so it joins straight to any copy of G-NAF with no link table.

The output folder (`--out`, default `./cadastre_out`) is a ready-to-upload dataset:

| File | Contents |
|------|----------|
| `<STATE>_parcels.parquet` | One row per parcel: source attributes, candidate parcel keys, the G-NAF columns below, a point inside the parcel and WKT geometry (EPSG:4326) |
| `<STATE>_parcels.csv` | The same columns as CSV (list columns as `\|`-separated text; `.csv.gz` with `--compress`) |
| `summary.csv` | Per-state counts, G-NAF match rates per candidate key, and licence |
| `ATTRIBUTION.md` | Source and licence list to ship with the data |
| `data_dictionary.md` / `data_dictionary.csv` | Every column of every file: type, description and an example value |
| `README.md` | Dataset README for Kaggle: files, coverage, usage examples, licences |
| `dataset-metadata.json` | Kaggle dataset metadata (title, licence, per-column descriptions) for `kaggle datasets create` |

G-NAF columns in each parcels file:

- `gnaf_legal_parcel_id`: the parcel key in G-NAF `LEGAL_PARCEL_ID` format
- `gnaf_key_matched`: `True` if that key actually exists in G-NAF
- `gnaf_address_count`: number of G-NAF addresses linked to the parcel
- `gnaf_address_detail_pids`: list of the linked G-NAF `ADDRESS_DETAIL_PID`s (null if none)
- `gnaf_link_methods`: how they were linked, `legal_parcel_id` and/or `spatial_within` (null if none)

Geometry-group columns (for stacked parcels such as strata lots that share one polygon):

- `geometry_group_id`: the lowest `source_oid` among parcels with an identical polygon
- `geometry_group_size`: how many parcels share that polygon (1 = unique)

Every state's files start with the same columns in the same order (`state`, `source_oid`, the G-NAF
and geometry-group columns, `point_lon`, `point_lat`), then the state's candidate keys and source
attributes, with `wkt` last. Columns are typed (integers, floats, booleans, dates, lists) from the source layers' field metadata.

Working files live in the work folder (`--work`, default `./cadastre_work`): the staged CSVs in
`staging/`, resume progress in `staging/_progress/` and the G-NAF zip. Downloads are **resumable**,
so re-running picks up where an interrupted run stopped.

## Data sources

| State | Source | Licence |
|-------|--------|---------|
| NSW | NSW Spatial Services | CC BY |
| VIC | Vicmap Property (DTP) | CC BY 4.0 |
| QLD | QSCF Land Parcel Property Framework | CC BY 4.0 |
| TAS | theLIST | CC BY 3.0 AU |
| ACT | ACTmapi | © ACT Government |
| WA | Landgate SLIP public (geometry only) | Personal-use terms |
| SA | *not open data*: supply your own copy with `--local` | Purchased from Land Services SA |
| NT | *not open data*: supply your own copy with `--local` | NTLIS |
| G-NAF | Geoscape via data.gov.au | CC BY 4.0 (Open G-NAF restriction) |

WA's public layer has no attributes, so WA addresses are linked with a **point-in-polygon spatial
join** instead of by key (see `--spatial-join`).

> Cadastral polygons are graphical representations only, not legal boundaries.

## Installation

The project is managed with [uv](https://docs.astral.sh/uv/). Python 3.10+ is required.

```bash
uv sync                    # core deps + dev tools (pytest, ruff, geopandas)
uv sync --extra geo        # add geopandas/shapely as a runtime extra only
```

`geopandas` and `shapely` are needed for the WA spatial join and for `--local` files. The core
download and key matching run without them.

## Usage

```bash
uv run cadastre-gnaf                                    # everything, all open states
uv run cadastre-gnaf --states NSW VIC --step download   # download only
uv run cadastre-gnaf --step gnaf                        # G-NAF matching + publish (after downloading)
uv run cadastre-gnaf --step publish                     # rewrite the Parquet files only
uv run cadastre-gnaf --step docs --kaggle-id me/au-cadastre   # rebuild README + data dictionary only
uv run cadastre-gnaf --compress --workers 8 --out D:/cadastre
uv run cadastre-gnaf --local SA=/data/sa/Parcel_Cadastre.shp --states SA
uv run python -m cadastre_gnaf --help                   # same CLI via the module
```

| Option | Default | Description |
|--------|---------|-------------|
| `--states` | all | States to build (SA/NT need `--local`) |
| `--step` | `all` | `download`, `gnaf` (matching + publish), `all`, `publish` (only the Parquet files), or `docs` (only the dataset docs) |
| `--out` | `./cadastre_out` | Output folder: the publishable dataset |
| `--work` | `./cadastre_work` | Working folder: staged CSVs, progress, G-NAF zip (about 2 GB) |
| `--compress` | off | Gzip the working and published CSVs |
| `--no-wkt` | off | Omit the WKT column (much smaller; disables the spatial join) |
| `--decimals` | `6` | Coordinate decimals (6 ≈ 0.1 m) |
| `--workers` | `4` | Parallel requests per state |
| `--page-size` | server max (≤ 2000) | Features per request |
| `--force` | off | Re-download states already marked done |
| `--gnaf-dir` | none | Use an already extracted G-NAF release |
| `--gnaf-zip-url` | latest GDA2020 | Specific G-NAF zip |
| `--spatial-join` | `WA` | States that also get a point-in-polygon address join |
| `--local STATE=PATH` | none | Licensed file (any format geopandas reads) instead of a web service |
| `--token STATE=TOKEN` | none | ArcGIS token for a subscription service (e.g. a SLIP layer) |
| `--kaggle-id` | `your-username/australian-cadastre-gnaf` | Kaggle dataset id written to `dataset-metadata.json` and used in the README's paths |

The process exits with code 1 if any state failed to download. Re-run the same command to resume.

## How it works

1. **Download** (`cadastre_gnaf.download`): reads each layer's ObjectID range, then fetches pages
   of `[lo, hi)` ObjectID ranges through a sliding window of parallel requests. Workers never wait
   on each other, so one slow or failing request doesn't stall the others, while pages are still
   written in ObjectID order so a resumed run starts at the right place. Truncated pages are split
   in half until the server returns them whole, and large gaps in the ObjectIDs are skipped. Esri JSON polygons are converted to
   WKT in pure Python, with a representative point that is guaranteed to lie inside the parcel.
2. **Key candidates** (`cadastre_gnaf.keys`): each state builds several candidate keys in G-NAF's
   `LEGAL_PARCEL_ID` format (for example `13/31993` or `11/C/3625` for NSW, `66/RP139841` for QLD).
3. **G-NAF matching** (`cadastre_gnaf.linking`): measures how many parcels each candidate matches,
   picks the first matching candidate per parcel, links G-NAF addresses to parcels by that key and
   rewrites the staged CSV with the G-NAF columns, including each parcel's address ids. States listed
   in `--spatial-join` also get a spatial join for addresses that the key did not link: each address
   goes to the smallest polygon containing its geocode, and to one parcel per stack of identical
   polygons (the stack's `geometry_group_id`).
4. **Publish** (`cadastre_gnaf.publish`): converts each staged CSV to a zstd-compressed Parquet file,
   typing every column from the data dictionary (the source layers' field types, lists for the
   G-NAF address ids), and copies the CSV alongside it. Both are built in the work folder and moved
   into the output folder only when complete.
5. **Report** (`cadastre_gnaf.report`): writes `summary.csv` and `ATTRIBUTION.md`, then the dataset
   docs: a data dictionary built from the Parquet schemas, sample values and the source layers'
   field metadata (aliases), a Kaggle README and `dataset-metadata.json`.

## Publishing to Kaggle

The output folder is a ready-to-upload Kaggle dataset. With the
[Kaggle CLI](https://github.com/Kaggle/kaggle-api) installed and `~/.kaggle/kaggle.json` in place:

```bash
uv run cadastre-gnaf --step docs --kaggle-id <your-kaggle-username>/australian-cadastre-gnaf
kaggle datasets create -p cadastre_out              # first upload
kaggle datasets version -p cadastre_out -m "Refresh" # later updates
```

The README is used as the dataset description, and the per-column descriptions appear in Kaggle's
data explorer.

## Project layout

Each module holds a single public function (or one small class or dataclass), and each has a
matching test file under `tests/`.

```
src/cadastre_gnaf/
├── config.py            Config dataclass (all run options)
├── constants.py         Shared constants (states, G-NAF ids, column names)
├── cli/                 build_parser, parse_state_pairs, parse_config, main
├── keys/                attr_value, norm_key, join_key, strip_zeros, key_names, keys_<state>
├── geometry/            esri_to_wkt and its helpers (rings, areas, centroid, WKT)
├── sources/             Source dataclass and the SOURCES registry
├── arcgis/              make_session, arcgis_get, layer_info, feature_count, oid_bounds, fetch_range
├── storage/             parcels_path, parquet_path, read/write_progress, append_csv
├── tabular/             output_columns, rows_from_items, features_to_items, epoch_ms_to_date
├── download/            page_size, fetch_in_order, download_arcgis_state, load_local_state, run_downloads
├── gnaf/                GnafSource, open_gnaf, open_table, read_table, read_address_*, download_file
├── linking/             score_keys, choose_keys, key_links, spatial_links, rewrite_parcels, finalise_state, run_gnaf
├── publish/             arrow_type, to_arrow, write_parquet, publish_state, run_publish
└── report/              summary_rows, attribution_markdown, write_summary, data dictionary and Kaggle docs
tests/                   mirrors src/ (one test_<module>.py per module)
```

### Using it as a library

```python
from pathlib import Path
from cadastre_gnaf.arcgis import make_session
from cadastre_gnaf.config import Config
from cadastre_gnaf.download import run_downloads

config = Config(states=("ACT",), out_dir=Path("out"), include_wkt=False)
run_downloads(config, make_session())
```

## Development

```bash
uv run pytest                      # run the tests
uv run pytest --cov=cadastre_gnaf  # with coverage
uv run ruff check .                # lint
```

The tests do not use the network. HTTP calls go through a fake session (see `tests/conftest.py`),
and G-NAF is mocked with a small in-memory zip.
