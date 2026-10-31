import pandas as pd

from cadastre_gnaf.publish.published_frame import published_frame
from cadastre_gnaf.publish.write_outputs import write_outputs
from cadastre_gnaf.report.describe_column import describe_column
from cadastre_gnaf.report.source_fields import source_fields
from cadastre_gnaf.storage import parcels_path, parquet_path, published_csv_path


def publish_state(config, session, state, source, chunk=200_000):
    """Publish a state's staged CSV as parquet/<STATE>_parcels.parquet and csv/<STATE>_parcels.csv.

    Columns are typed from the data dictionary. Returns the rows written, or None without a staged CSV.
    """
    staged = parcels_path(config, state)
    if not staged.exists():
        return None
    header = published_frame(pd.read_csv(staged, nrows=0, dtype=str), state)       # final columns, no rows
    fields = source_fields(config, session, state, source)
    kinds = {c: describe_column(c, state, fields)[0] for c in header.columns}
    out, csv_out = parquet_path(config, state), published_csv_path(config, state)
    out.parent.mkdir(parents=True, exist_ok=True)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    frames = (published_frame(c, state)
              for c in pd.read_csv(staged, dtype=str, keep_default_na=False, chunksize=chunk))
    rows = write_outputs(frames, kinds, out, csv_out, config.staging_dir, config.compression)
    print(f"[{state}] published {rows:,} parcels -> {out.name} ({out.stat().st_size / 1e6:,.1f} MB), "
          f"{csv_out.name} ({csv_out.stat().st_size / 1e6:,.1f} MB)")
    return rows
