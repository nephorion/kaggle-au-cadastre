import shutil

import pandas as pd

from cadastre_gnaf.publish.write_parquet import write_parquet
from cadastre_gnaf.report.describe_column import describe_column
from cadastre_gnaf.report.source_fields import source_fields
from cadastre_gnaf.storage import parcels_path, parquet_path, published_csv_path


def publish_state(config, session, state, source):
    """Publish the staged CSV as <STATE>_parcels.parquet (typed from the data dictionary) and as a CSV copy.

    Both are built in the staging folder and moved into the output folder when complete.

    Returns the rows written, or None if the state has no staged CSV.
    """
    staged = parcels_path(config, state)
    if not staged.exists():
        return None
    columns = pd.read_csv(staged, nrows=0).columns     # header only: type every column up front
    fields = source_fields(config, session, state, source)
    kinds = {c: describe_column(c, state, fields)[0] for c in columns}
    out = parquet_path(config, state)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = write_parquet(staged, out, kinds, tmp=config.staging_dir / (out.name + ".tmp"))
    csv_out = published_csv_path(config, state)
    tmp = config.staging_dir / (csv_out.name + ".tmp")
    shutil.copyfile(staged, tmp)
    shutil.move(tmp, csv_out)
    print(f"[{state}] published {rows:,} parcels -> {out.name} ({out.stat().st_size / 1e6:,.1f} MB), "
          f"{csv_out.name} ({csv_out.stat().st_size / 1e6:,.1f} MB)")
    return rows
