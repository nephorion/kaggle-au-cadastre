# cadastre-gnaf

Download Australian state **cadastres** (land parcels) from public ArcGIS REST services and write
**one flat CSV per state**, with each parcel keyed to **G-NAF** (the Geocoded National Address File)
through its `LEGAL_PARCEL_ID`.

For every state you get:

| File | Contents |
|------|----------|
| `<STATE>_parcels.csv` | One row per parcel: source attributes, a point inside the parcel, WKT geometry (EPSG:4326), the candidate parcel keys and the three G-NAF columns below |
| `<STATE>_gnaf_address_parcel_links.csv` | Address → parcel link table (`address_detail_pid`, `legal_parcel_id`, `source_oid`, `method`) |
| `summary.csv` | Per-state counts, G-NAF match rates per candidate key, and licence |
| `ATTRIBUTION.md` | Source and licence list to ship with the data |

G-NAF columns added to each parcels CSV:

- `gnaf_legal_parcel_id`: the parcel key in G-NAF format
- `gnaf_key_matched`: `True` if that key actually exists in G-NAF
- `gnaf_address_count`: number of G-NAF addresses linked to the parcel

Downloads are **resumable**: progress is saved per state in `<out>/_progress/`, so re-running
picks up where an interrupted run stopped.

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
uv run cadastre-gnaf --step gnaf                        # G-NAF matching only (after downloading)
uv run cadastre-gnaf --compress --workers 8 --out D:/cadastre
uv run cadastre-gnaf --local SA=/data/sa/Parcel_Cadastre.shp --states SA
uv run python -m cadastre_gnaf --help                   # same CLI via the module
```

| Option | Default | Description |
|--------|---------|-------------|
| `--states` | all | States to build (SA/NT need `--local`) |
| `--step` | `all` | `download`, `gnaf`, or `all` |
| `--out` | `./cadastre_out` | Output folder |
| `--work` | `./cadastre_work` | Scratch folder (G-NAF zip, about 1.5 GB) |
| `--compress` | off | Write `.csv.gz` |
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

The process exits with code 1 if any state failed to download. Re-run the same command to resume.

## How it works

1. **Download** (`cadastre_gnaf.download`): reads each layer's ObjectID range, then fetches pages
   of `[lo, hi)` ObjectID ranges in parallel. Truncated pages are split in half until the server
   returns them whole, and gaps in the ObjectIDs are skipped. Esri JSON polygons are converted to
   WKT in pure Python, with a representative point that is guaranteed to lie inside the parcel.
2. **Key candidates** (`cadastre_gnaf.keys`): each state builds several candidate keys in G-NAF's
   `LEGAL_PARCEL_ID` format (for example `13/31993` or `11/C/3625` for NSW, `66/RP139841` for QLD).
3. **G-NAF matching** (`cadastre_gnaf.linking`): measures how many parcels each candidate matches,
   picks the first matching candidate per parcel, writes the address link table and rewrites the
   parcels CSV with the G-NAF columns. States listed in `--spatial-join` also get a spatial join for
   addresses that the key did not link.
4. **Report** (`cadastre_gnaf.report`): writes `summary.csv` and `ATTRIBUTION.md`.

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
├── storage/             parcels_path, links_path, read/write_progress, append_csv
├── tabular/             output_columns, rows_from_items, features_to_items, epoch_ms_to_date
├── download/            page_size, page_ranges, download_arcgis_state, load_local_state, run_downloads
├── gnaf/                GnafSource, open_gnaf, open_table, read_table, read_address_*, download_file
├── linking/             score_keys, choose_keys, key_links, spatial_links, rewrite_parcels, finalise_state, run_gnaf
└── report/              summary_rows, attribution_markdown, write_summary
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
