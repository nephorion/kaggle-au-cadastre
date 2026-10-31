import pandas as pd
import pyarrow.parquet as pq

from cadastre_gnaf.constants import DEFAULT_STATES
from cadastre_gnaf.storage import parquet_path, published_csv_path


def dataset_files(config):
    """The data files in the output folder: path (relative, e.g. `parquet/NSW_parcels.parquet`), state, kind,
    rows, size in MB and a description.

    Covers every state with a published file, not just the states of this run. A state's CSV has the
    same columns as its Parquet file; its `same_as` names that file.
    """
    files = []
    for st in DEFAULT_STATES:
        path, csv = parquet_path(config, st), published_csv_path(config, st)
        if not path.exists():
            continue
        rows = pq.ParquetFile(path).metadata.num_rows
        text = f"{st} land parcels: source attributes, G-NAF key and address ids, interior point and WKT geometry"
        files.append({"file": path.relative_to(config.out_dir).as_posix(), "state": st, "kind": "parcels", "rows": rows,
                      "size_mb": round(path.stat().st_size / 1e6, 1), "description": text})
        if csv.exists():
            files.append({"file": csv.relative_to(config.out_dir).as_posix(), "state": st, "kind": "parcels_csv",
                          "rows": rows, "size_mb": round(csv.stat().st_size / 1e6, 1),
                          "same_as": path.relative_to(config.out_dir).as_posix(),
                          "description": f"{text} (CSV; list columns are pipe-separated)"})
    summary = config.out_dir / "summary.csv"
    if summary.exists():
        files.append({"file": summary.name, "state": None, "kind": "summary", "rows": len(pd.read_csv(summary)),
                      "size_mb": round(summary.stat().st_size / 1e6, 3),
                      "description": "Per-state counts, G-NAF match rates and licences"})
    return files
