from cadastre_gnaf.report.count_rows import count_rows
from cadastre_gnaf.storage import links_path, parcel_addresses_path, parcels_path


def dataset_files(config):
    """The data files in the output folder: name, state, kind, rows, size in MB and a description."""
    files = []
    for st in config.states:
        for kind, path, text in (
                ("parcels", parcels_path(config, st), f"{st} land parcels: keys, G-NAF columns, "
                                                      "source attributes, interior point and WKT geometry"),
                ("links", links_path(config, st), f"{st} G-NAF address -> parcel links"),
                ("parcel_addresses", parcel_addresses_path(config, st),
                 f"{st} parcels with their G-NAF addresses inline: one row per parcel and address, "
                 "empty address columns where none is linked")):
            if path.exists():
                files.append({"file": path.name, "state": st, "kind": kind, "rows": count_rows(path),
                              "size_mb": round(path.stat().st_size / 1e6, 1), "description": text})
    summary = config.out_dir / "summary.csv"
    if summary.exists():
        files.append({"file": summary.name, "state": None, "kind": "summary", "rows": count_rows(summary),
                      "size_mb": round(summary.stat().st_size / 1e6, 3),
                      "description": "Per-state counts, G-NAF match rates and licences"})
    return files
