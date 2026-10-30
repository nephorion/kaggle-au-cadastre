import shutil

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.publish.arrow_type import arrow_type
from cadastre_gnaf.publish.to_arrow import to_arrow


def write_parquet(csv_path, out_path, kinds, chunk=200_000, compression="zstd", tmp=None):
    """Convert a CSV to Parquet in chunks; `kinds` maps column -> dictionary type. Returns the rows written.

    The file is built at `tmp` (default: next to `out_path`) and moved into place only when complete.
    """
    tmp = tmp or out_path.with_name(out_path.name + ".tmp")
    writer, rows = None, 0
    try:
        for c in pd.read_csv(csv_path, dtype=str, keep_default_na=False, chunksize=chunk):
            if writer is None:
                schema = pa.schema([(col, arrow_type(kinds.get(col))) for col in c.columns])
                writer = pq.ParquetWriter(tmp, schema, compression=compression)
            writer.write_table(pa.Table.from_arrays(
                [to_arrow(c[f.name], kinds.get(f.name)) for f in schema], schema=schema))
            rows += len(c)
    finally:
        if writer is not None:
            writer.close()
    if writer is None:
        return 0
    shutil.move(tmp, out_path)                          # a rename unless the folders are on different drives
    return rows
