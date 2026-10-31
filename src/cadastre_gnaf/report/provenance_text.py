from cadastre_gnaf.constants import REPO_URL
from cadastre_gnaf.report.kaggle_readme_markdown import GNAF_DATA_GOV_URL


def provenance_text(files, sources):
    """Kaggle "Sources" (provenance): each published state's service and licence, G-NAF, and how it was collected."""
    states = [f["state"] for f in files if f["kind"] == "parcels"]
    lines = ["Sources:"]
    lines += [f"- {st} cadastre: {sources[st].url or 'licensed local file'} ({sources[st].licence})"
              for st in states if st in sources]
    lines += [f"- G-NAF (Geoscape Geocoded National Address File), GDA2020 release: {GNAF_DATA_GOV_URL}", "",
              "Collection: every parcel was downloaded from each state's public ArcGIS REST service in ObjectID "
              "pages, linked to G-NAF addresses by legal parcel id (and by point in polygon for WA), harmonised "
              f"and published as Parquet and CSV by {REPO_URL}."]
    return "\n".join(lines)
