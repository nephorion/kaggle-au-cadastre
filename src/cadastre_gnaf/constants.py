"""Shared constants."""

DEFAULT_STATES = ("NSW", "VIC", "QLD", "TAS", "ACT", "WA", "SA", "NT")

# data.gov.au "Geoscape G-NAF" package
GNAF_PACKAGE_ID = "19432f89-dc3a-4ef3-b943-5326ef1dbecc"
GNAF_PACKAGE_API = "https://data.gov.au/data/api/3/action/package_show"

USER_AGENT = "kaggle-au-cadastre-notebook/1.0 (research; polite paging)"

# Columns this tool writes itself; source attributes with the same name get a "src_" prefix.
GNAF_COLUMNS = ("gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count")
BASE_COLUMNS = frozenset({"state", "source_oid", "point_lon", "point_lat", "wkt", *GNAF_COLUMNS})

LINK_COLUMNS = ["address_detail_pid", "legal_parcel_id", "source_oid", "method"]
