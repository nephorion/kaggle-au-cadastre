# cadastre-gnaf

Download Australian state **cadastres** (land parcels) from public ArcGIS REST services and publish
**one Parquet and one CSV file per state**. Each parcel carries the ids of its **G-NAF** (Geocoded National
Address File) addresses, so it joins straight to any copy of G-NAF with no link table.

The output folder (`--out`, default `./cadastre_out`) is a ready-to-upload dataset:

| File | Contents |
|------|----------|
| `<STATE>_parcels.parquet` | One row per parcel in the [layout below](#file-layout): G-NAF columns, harmonised columns, the state's own attributes and WKT geometry (EPSG:4326) |
| `<STATE>_parcels.csv` | The same columns as CSV (list columns as `\|`-separated text; `.csv.gz` with `--compress`) |
| `summary.csv` | Per-state counts, G-NAF match rates per candidate key, and licence |
| `ATTRIBUTION.md` | Source and licence list to ship with the data |
| `data_dictionary.md` / `data_dictionary.csv` | Every column of every file: type, description and an example value |
| `README.md` | Dataset README for Kaggle: files, coverage, usage examples, licences |
| `dataset-metadata.json` | Kaggle dataset metadata (title, licence, per-column descriptions) for `kaggle datasets create` |

## File layout

Each state is published in its own files (`<STATE>_parcels.parquet` and `<STATE>_parcels.csv`), and every
file has the same layout, so states can be read with the same code or stacked into one table:

1. **Identity, G-NAF and geometry-group columns**, the same in every state
2. **Harmonised columns**, the same in every state, null where the state does not publish the information
3. **`src_*` columns**: the state's own attributes as published, renamed to lower-case snake case
   (`TENURE_TY` → `src_tenure_ty`). These differ between states.
4. **`wkt`**: the polygon (EPSG:4326)

Columns are typed in Parquet (integers, floats, booleans, dates, lists). In the CSV, lists are
`|`-separated text.

### 1. Identity, G-NAF and geometry groups

- `state`, `source_oid` (the parcel's ObjectID in the source service)
- `gnaf_legal_parcel_id`: the parcel key in G-NAF `LEGAL_PARCEL_ID` format
- `gnaf_key_matched`: `True` if that key actually exists in G-NAF
- `gnaf_address_count`: number of G-NAF addresses linked to the parcel
- `gnaf_address_detail_pids`: list of the linked G-NAF `ADDRESS_DETAIL_PID`s (null if none)
- `gnaf_link_methods`: how they were linked, `legal_parcel_id` and/or `spatial_within` (null if none)
- `geometry_group_id`: the lowest `source_oid` among parcels with an identical polygon (stacked strata lots)
- `geometry_group_size`: how many parcels share that polygon (1 = unique)
- `point_lon`, `point_lat`: a point guaranteed to lie inside the parcel

### 2. Harmonised columns

| Column | Type | Description |
|---|---|---|
| `lot` | string | Lot number (ACT: block number). |
| `section` | string | Section number. |
| `plan` | string | Plan the lot is on, with its type prefix, e.g. `DP246488`, `PS936577`, `SP12345`. |
| `parcel_label` | string | The state's own human-readable parcel identifier, e.g. NSW `1//DP12345`, VIC `1\PS936577`, QLD `4SE1`, TAS `207296/1`, ACT `TUGG/COND/160/32`. |
| `title_ref` | string | Certificate of title reference as `volume/folio` (TAS, ACT). |
| `status` | string | `current`, `proposed` or `retired`. |
| `tenure` | string | `freehold`, `lease`, `crown`, `council`, `commonwealth` or `other`. |
| `is_strata` | boolean | True for strata / volumetric lots (lots in a building or above/below ground). |
| `is_road` | boolean | True for road and footway parcels. |
| `is_multipart` | boolean | True if the parcel polygon has more than one part. |
| `area_m2` | number | Area of the polygon in m², computed in Australian Albers equal-area (EPSG:3577). Comparable across states. |
| `perimeter_m` | number | Perimeter of the polygon in metres, computed in EPSG:3577. |
| `stated_area_m2` | number | Area stated or measured by the state (survey / title area), in m². |
| `locality` | string | Suburb or locality (upper case): the most common locality of the parcel's G-NAF addresses, else the state's own locality field. |
| `feature_name` | string | Name of the parcel or feature (e.g. a park, reserve or property name). |
| `source_feature_id` | string | The state's persistent feature id, stable across releases (e.g. NSW `cadid`, VIC `parcel_pfi`). |
| `source_created` | date | Date the state created the parcel record. |
| `source_last_updated` | date | Date the state last changed the parcel record. |

Where each harmonised column comes from, per state (`polygon` = computed from the geometry; – = the
state does not publish it, so the column is always null there):

| Column | NSW | VIC | QLD | TAS | ACT | WA |
|---|---|---|---|---|---|---|
| `lot` | `src_lotnumber` | `src_parcel_lot_number` | `src_lot` | – | `src_block_number` | – |
| `section` | `src_sectionnumber` | `src_parcel_sec` | – | – | `src_section_number` | – |
| `plan` | `src_planlabel` | `src_parcel_plan_number` | `src_plan` | – | `DP` + `src_deposited_plan_no` | – |
| `parcel_label` | `src_lotidstring` | `src_parcel_spi` | `src_lotplan` | `src_volume` + `/` + `src_folio` | `src_district_short` + `/` + `src_division_short` + `/` + `src_section_number` + `/` + `src_block_number` | – |
| `title_ref` | – | – | – | `src_volume` + `/` + `src_folio` | `src_volume_folio` with `:` → `/` | – |
| `status` | always `current` | `src_parcel_status` (A → current, P → proposed) | `src_parcel_state` (Created → current, Existing → current) | always `current` | `src_current_lifecycle_stage` (REGISTERED → current, APPROVED → proposed, PROPOSED → proposed, RETIRED → retired) | – |
| `tenure` | – | `src_parcel_crown_status` (C → crown, G → null) | `src_tenure`, translated (codes below) | `src_tenure_ty`, translated (codes below) | always `lease` | – |
| `is_strata` | – | – | `src_is_volumetric` matches `^Yes$` | `src_strata_lev` matches `^(?!Not Applicable$)` | `src_stratum_datum_id` is present | – |
| `is_road` | – | `src_parcel_road` matches `^Y$` | – | `src_cad_type2` matches `Road\|Footway` | – | – |
| `is_multipart` | polygon | polygon | polygon | polygon | polygon | polygon |
| `area_m2` | polygon | polygon | polygon | polygon | polygon | polygon |
| `perimeter_m` | polygon | polygon | polygon | polygon | polygon | polygon |
| `stated_area_m2` | `src_planlotarea` in `src_planlotareaunits` units, as m² | – | `src_statedarea` in `src_statedareaunit` units, as m² | `src_meas_area`, as m² | `src_block_leased_area`, as m² | – |
| `locality` | G-NAF | G-NAF | G-NAF, else `src_locality` | G-NAF | G-NAF, else `src_division_name` | G-NAF |
| `feature_name` | – | – | `src_feat_name` | `src_feat_name`, else `src_prop_name` | – | – |
| `source_feature_id` | `src_cadid` | `src_parcel_pfi` | `src_uniqueid` | `src_cid` | `src_id` | – |
| `source_created` | `src_createdate` | `src_parcel_pfi_created` | – | – | – | – |
| `source_last_updated` | `src_lastupdate` | `src_parcel_ufi_created` | `src_last_edited_date` | – | `src_last_update` | – |

**QLD `tenure`** from `src_tenure`: Freehold → freehold; Lands Lease → lease; Mines Tenure → lease; Reserve → crown; State Land → crown; National Park → crown; State Forest → crown; Timber Reserve → crown; Water Resource → crown; Railway → crown; Housing Land → crown; Port and Harbours Boards → crown; Industrial Estates → crown; Commonwealth Acquisition → commonwealth, anything else → other.

**TAS `tenure`** from `src_tenure_ty`: Freehold Title → freehold; Horizontal Strata → freehold; Vertical Strata → freehold; Body Corporate → freehold; Share Title → freehold; Vertical Subdivision → freehold; Crown Land → crown; Tidal Crown Land → crown; Marine Crown Land → crown; Council → council; Commonwealth of Australia → commonwealth; Unknown → null; Not Applicable → null, anything else → other.

The mapping is defined in [field_map.py](src/cadastre_gnaf/publish/field_map.py) as small declarative
specs (a source column, a code translation, a join, an area with units…). To change how a state fills a
harmonised column, edit its entry there and run `cadastre-gnaf --step publish`. The tables in this README
and in the dataset README are generated from the same specs (`cadastre_gnaf.publish.mapping_markdown`).

### 3. Source columns

The `src_*` columns keep every attribute the state publishes, except:

- the layer's ObjectID copy (`OBJECTID` / `objectid`), which is `source_oid`
- `Shape__Area` / `Shape__Length` and similar, which each service computes in its own projection; use
  `area_m2` / `perimeter_m` instead
- the candidate G-NAF keys (`key_*`), working columns of the matching step; the chosen key is
  `gnaf_legal_parcel_id`, and the match rate of every candidate is in `summary.csv`

Every column of every file is described in the generated `data_dictionary.md`.

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
uv sync                    # core deps + dev tools (pytest, ruff, geopandas, kaggle CLI)
uv sync --extra geo        # add geopandas/shapely as a runtime extra only
```

`geopandas` and `shapely` are needed for the WA spatial join and for `--local` files. The core
download and key matching run without them.

## Usage

```bash
uv run cadastre-gnaf                                    # everything, all open states
uv run cadastre-gnaf --states NSW VIC --step download   # download only
uv run cadastre-gnaf --step gnaf                        # G-NAF matching + publish (after downloading)
uv run cadastre-gnaf --step publish                     # rewrite the Parquet + CSV files only
uv run cadastre-gnaf --step docs --kaggle-id me/au-cadastre   # rebuild README + data dictionary only
uv run cadastre-gnaf --compress --workers 8 --out D:/cadastre
uv run cadastre-gnaf --local SA=/data/sa/Parcel_Cadastre.shp --states SA
uv run python -m cadastre_gnaf --help                   # same CLI via the module
```

| Option | Default | Description |
|--------|---------|-------------|
| `--states` | all | States to build (SA/NT need `--local`) |
| `--step` | `all` | `download`, `gnaf` (matching + publish), `all`, `publish` (only the Parquet + CSV files), or `docs` (only the dataset docs) |
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
| `--kaggle-id` | `your-kaggle-username/australian-cadastre-gnaf` | Kaggle dataset id written to `dataset-metadata.json` and used in the README's paths |
| `--gnaf-kaggle-id` | `your-kaggle-username/gnaf-aug-2026-all-states-gda2020-flat` | Flat G-NAF Kaggle dataset (one CSV row per address) used in the dataset README's join example |

The process exits with code 1 if any state failed to download. Re-run the same command to resume.

## Regenerating the dataset

The pipeline keeps its intermediate results in the work folder, so a re-run only redoes what is
needed. Pick the command by what changed:

| What changed | Command | Redoes | Time (all states) |
|---|---|---|---|
| Nothing yet: first build | `uv run cadastre-gnaf` | download, G-NAF matching, publish, docs | a few hours (downloads) |
| The output layout or a harmonised mapping (`publish/field_map.py`, column code) | `uv run cadastre-gnaf --step publish` | Parquet + CSV files and docs, from the staged CSVs | ~15 min |
| The G-NAF matching or linking code, or a new G-NAF release | `uv run cadastre-gnaf --step gnaf` | matching, then publish and docs | ~30 min |
| Only README / data dictionary / Kaggle id | `uv run cadastre-gnaf --step docs --kaggle-id <user>/<slug>` | docs only | seconds |
| The states' data (fresh snapshot from the servers) | `uv run cadastre-gnaf --force` | everything, re-downloading every state | a few hours |
| A download was interrupted | re-run the same command | continues where it stopped | |

All of these take `--states` to limit the run, e.g. `uv run cadastre-gnaf --states VIC --step gnaf`.
That is safe: `summary.csv`, the README and the data dictionary always cover every state in the output
folder, using the saved figures of the states not in the run.

**Run large states one at a time.** On Windows we have seen an occasional native crash (segmentation
fault) in pandas/pyarrow while one process handles several multi-million-row states in a row. A run per
state avoids it, and a failed state can simply be re-run:

```bash
for s in ACT TAS QLD NSW VIC WA; do uv run cadastre-gnaf --states $s --step gnaf; done
```

```powershell
foreach ($s in "ACT","TAS","QLD","NSW","VIC","WA") { uv run cadastre-gnaf --states $s --step gnaf }
```

A failed or interrupted step never leaves partial files: staged CSVs are rewritten through a `.tmp`
file, and the published files are built in the work folder and moved into `cadastre_out` only when
complete. If a state fails, the previous version of its files stays in place.

Then [publish to Kaggle](#publishing-to-kaggle) (`kaggle datasets version` for an update).

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
   It also records each parcel's most common G-NAF locality and groups identical polygons.
4. **Publish** (`cadastre_gnaf.publish`): turns each staged CSV into the [shared layout](#file-layout):
   fills the harmonised columns from the state's fields (`field_map.py`), measures area and perimeter in
   Australian Albers (EPSG:3577), renames the state's attributes to `src_*` and drops the redundant ones.
   It then writes a zstd-compressed Parquet file, typed from the data dictionary, and a CSV with the
   same columns. Both are built in the work folder and moved into the output folder only when complete.
5. **Report** (`cadastre_gnaf.report`): writes `summary.csv` and `ATTRIBUTION.md`, then the dataset
   docs: a data dictionary built from the Parquet schemas, sample values and the source layers'
   field metadata (aliases), a Kaggle README and `dataset-metadata.json`.

## Publishing to Kaggle

The output folder is a ready-to-upload Kaggle dataset. The [Kaggle CLI](https://github.com/Kaggle/kaggle-api)
is a dev dependency, so `uv sync` installs it and `uv run kaggle` runs it.

1. Get an API token: on kaggle.com go to **Settings → API → Create New Token** and save the downloaded
   `kaggle.json` as `~/.kaggle/kaggle.json` (Windows: `C:\Users\<you>\.kaggle\kaggle.json`). It holds
   your username and key; keep it out of the repository.
2. Choose the dataset id `<your-kaggle-username>/<slug>`. Your username is the last part of your
   profile address (`kaggle.com/<username>`); the slug is any lower-case name with hyphens.
3. Write the id into the metadata and upload:

```bash
uv run cadastre-gnaf --step docs --kaggle-id <your-kaggle-username>/australian-cadastre-gnaf
uv run kaggle datasets create -p cadastre_out                 # first upload
uv run kaggle datasets version -p cadastre_out -m "Refresh"   # later updates
```

`dataset-metadata.json` is what the CLI reads, and `kaggle datasets create` requires it: the dataset
id, title, licence, the README as the dataset description, and a description of every column (shown in
Kaggle's data explorer).

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
├── tabular/             output_columns, rows_from_items, features_to_items, epoch_ms_to_date, source_column_name
├── download/            page_size, fetch_in_order, download_arcgis_state, load_local_state, run_downloads
├── gnaf/                GnafSource, open_gnaf, open_table, read_table, read_address_*, download_file
├── linking/             score_keys, choose_keys, key_links, spatial_links, geometry_groups, parcel_localities,
│                        rewrite_parcels, finalise_state, run_gnaf
├── publish/             field_map (per-state harmonisation), field_value, geometry_measures, harmonised_columns,
│                        published_frame, to_arrow, write_outputs, publish_state, run_publish, mapping_markdown
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
