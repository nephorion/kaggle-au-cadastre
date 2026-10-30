import argparse

from cadastre_gnaf.constants import DEFAULT_STATES

EPILOG = """\
examples:
  cadastre-gnaf                                    # everything, all open states
  cadastre-gnaf --states NSW VIC --step download
  cadastre-gnaf --step gnaf                        # G-NAF matching only (after downloading)
  cadastre-gnaf --step publish                     # rewrite the Parquet files only (after gnaf)
  cadastre-gnaf --step docs --kaggle-id me/au-cadastre   # rebuild README + data dictionary only
  cadastre-gnaf --compress --workers 8 --out D:/cadastre
  cadastre-gnaf --local SA=/data/sa/Parcel_Cadastre.shp --states SA
"""


def build_parser():
    ap = argparse.ArgumentParser(prog="cadastre-gnaf",
                                 description="Australian cadastres -> per-state CSV keyed to G-NAF",
                                 epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--states", nargs="+", default=list(DEFAULT_STATES),
                    help="states to build (default: all; SA/NT need --local)")
    ap.add_argument("--step", choices=["all", "download", "gnaf", "publish", "docs"], default="all",
                    help="download parcels, G-NAF matching (+ publish), everything (default), only publish the "
                         "Parquet files, or only the dataset docs")
    ap.add_argument("--out", default="./cadastre_out", help="output folder: the publishable dataset")
    ap.add_argument("--work", default="./cadastre_work",
                    help="working folder: staged CSVs, resume progress and the G-NAF zip (~2 GB)")
    ap.add_argument("--compress", action="store_true", help="gzip the staged working CSVs")
    ap.add_argument("--no-wkt", action="store_true", help="omit the WKT geometry column (much smaller)")
    ap.add_argument("--decimals", type=int, default=6, help="coordinate decimals in WKT (default 6, ~0.1 m)")
    ap.add_argument("--workers", type=int, default=4, help="parallel requests per state (default 4)")
    ap.add_argument("--page-size", type=int, default=None,
                    help="features per request (default: server max, capped at 2000)")
    ap.add_argument("--force", action="store_true", help="re-download states already marked done")
    ap.add_argument("--gnaf-dir", default=None, help="folder with an extracted G-NAF release (skips the download)")
    ap.add_argument("--gnaf-zip-url", default=None, help="specific G-NAF zip URL (default: latest GDA2020 release)")
    ap.add_argument("--spatial-join", nargs="*", default=["WA"],
                    help="states that also get a point-in-polygon address join (default: WA)")
    ap.add_argument("--local", nargs="*", default=[], metavar="STATE=PATH",
                    help="licensed/purchased data to use instead of a web service, e.g. SA=/data/sa.shp")
    ap.add_argument("--token", nargs="*", default=[], metavar="STATE=TOKEN",
                    help="ArcGIS token for a subscription service, e.g. WA=<SLIP token>")
    ap.add_argument("--kaggle-id", default="your-kaggle-username/australian-cadastre-gnaf",
                    help="Kaggle dataset id (owner/slug) written to dataset-metadata.json and the README")
    ap.add_argument("--gnaf-kaggle-id", default="your-kaggle-username/gnaf-aug-2026-all-states-gda2020-flat",
                    help="Kaggle dataset with flat G-NAF (one CSV row per address) used in the README's join example")
    return ap
