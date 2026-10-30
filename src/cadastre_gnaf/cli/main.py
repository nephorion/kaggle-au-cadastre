import csv
import time

from cadastre_gnaf.arcgis import make_session
from cadastre_gnaf.cli.parse_config import parse_config
from cadastre_gnaf.download import run_downloads
from cadastre_gnaf.linking import run_gnaf
from cadastre_gnaf.publish import run_publish
from cadastre_gnaf.report import write_dataset_docs, write_summary


def main(argv=None):
    """Entry point: download, match to G-NAF, publish Parquet, summarise and document, as selected by --step."""
    config = parse_config(argv)
    csv.field_size_limit(2**31 - 1)                    # WKT fields can be very large
    config.out_dir.mkdir(parents=True, exist_ok=True)
    config.work_dir.mkdir(parents=True, exist_ok=True)
    print("output ->", config.out_dir.resolve(), "| scratch ->", config.work_dir.resolve())

    session = make_session()
    t0 = time.time()
    failures, summaries = {}, []
    if config.do_download:
        failures = run_downloads(config, session)
    if config.do_gnaf:
        summaries = run_gnaf(config, session)
    if config.do_publish:
        run_publish(config, session)
    if config.step not in ("publish", "docs"):
        write_summary(config, summaries)
    write_dataset_docs(config, session)
    print(f"finished in {(time.time() - t0) / 3600:.2f} h" + (f"; failed: {list(failures)}" if failures else ""))
    return 1 if failures else 0
