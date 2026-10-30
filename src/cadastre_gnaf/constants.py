"""Shared constants."""

DEFAULT_STATES = ("NSW", "VIC", "QLD", "TAS", "ACT", "WA", "SA", "NT")

# data.gov.au "Geoscape G-NAF" package
GNAF_PACKAGE_ID = "19432f89-dc3a-4ef3-b943-5326ef1dbecc"
GNAF_PACKAGE_API = "https://data.gov.au/data/api/3/action/package_show"

USER_AGENT = "kaggle-au-cadastre-notebook/1.0 (research; polite paging)"

# Columns this tool writes itself; source attributes with the same name get a "src_" prefix.
GNAF_COLUMNS = ("gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count", "gnaf_address_detail_pids",
                "gnaf_link_methods")
GEOMETRY_GROUP_COLUMNS = ("geometry_group_id", "geometry_group_size")
BASE_COLUMNS = frozenset({"state", "source_oid", "point_lon", "point_lat", "wkt", *GNAF_COLUMNS,
                          *GEOMETRY_GROUP_COLUMNS})

# Columns every published parcels file starts with, in this order; the state's candidate keys and
# source attributes follow, and `wkt` comes last.
LEADING_COLUMNS = ("state", "source_oid", *GNAF_COLUMNS, *GEOMETRY_GROUP_COLUMNS, "point_lon", "point_lat")

# Separator of list values (address ids, link methods) in the staged CSVs; lists in the Parquet output.
LIST_SEPARATOR = "|"
