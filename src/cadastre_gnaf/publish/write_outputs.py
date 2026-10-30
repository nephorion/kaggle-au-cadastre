import shutil

import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.publish.arrow_type import arrow_type
from cadastre_gnaf.publish.to_arrow import to_arrow


def write_outputs(frames, kinds, parquet_out, csv_out, work_dir, csv_compression=None, compression="zstd"):
    """Write text chunks to a typed Parquet file and a CSV with the same columns. Returns the rows written.

    `kinds` maps column -> dictionary type. Both files are built in `work_dir` and moved into place only
    when complete, so the output folder never holds partial files.
    """
    tmp_parquet, tmp_csv = work_dir / (parquet_out.name + ".tmp"), work_dir / (csv_out.name + ".tmp")
    tmp_parquet.unlink(missing_ok=True)                 # leftovers of an interrupted run
    tmp_csv.unlink(missing_ok=True)
    writer, schema, rows = None, None, 0
    try:
        for c in frames:
            first = writer is None
            if first:
                schema = pa.schema([(col, arrow_type(kinds.get(col))) for col in c.columns])
                writer = pq.ParquetWriter(tmp_parquet, schema, compression=compression)
            writer.write_table(pa.Table.from_arrays([to_arrow(c[f.name], kinds.get(f.name)) for f in schema],
                                                    schema=schema))
            c.to_csv(tmp_csv, mode="w" if first else "a", header=first, index=False, compression=csv_compression)
            rows += len(c)
    finally:
        if writer is not None:
            writer.close()
    if writer is None:
        return 0
    shutil.move(tmp_parquet, parquet_out)                # a rename unless the folders are on different drives
    shutil.move(tmp_csv, csv_out)
    return rows
