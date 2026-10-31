"""Shared constants."""

DEFAULT_STATES = ("NSW", "VIC", "QLD", "TAS", "ACT", "WA", "SA", "NT")

# data.gov.au "Geoscape G-NAF" package
GNAF_PACKAGE_ID = "19432f89-dc3a-4ef3-b943-5326ef1dbecc"
GNAF_PACKAGE_API = "https://data.gov.au/data/api/3/action/package_show"

# Placeholder Kaggle dataset id; `kaggle datasets create` rejects it until --kaggle-id names a real one.
DEFAULT_KAGGLE_ID = "your-kaggle-username/australian-cadastre-gnaf"

# Environment variables CADASTRE_TOKEN_<STATE> supply ArcGIS tokens without putting them on the command line.
TOKEN_ENV_PREFIX = "CADASTRE_TOKEN_"

USER_AGENT ="kaggle-au-cadastre-notebook/1.0 (research; polite paging)"

# Columns this tool writes itself; source attributes with the same name get a "src_" prefix.
GNAF_COLUMNS = ("gnaf_legal_parcel_id", "gnaf_key_matched", "gnaf_address_count", "gnaf_address_detail_pids",
                "gnaf_link_methods")
GEOMETRY_GROUP_COLUMNS = ("geometry_group_id", "geometry_group_size")
BASE_COLUMNS = frozenset({"state", "source_oid", "point_lon", "point_lat", "wkt", *GNAF_COLUMNS,
                          *GEOMETRY_GROUP_COLUMNS})

# Columns every published parcels file starts with, in this order.
LEADING_COLUMNS = ("state", "source_oid", *GNAF_COLUMNS, *GEOMETRY_GROUP_COLUMNS, "point_lon", "point_lat")

# Harmonised columns, the same in every state (null where a state has no such information); they
# follow LEADING_COLUMNS. The state's own attributes come next as `src_*` columns, and `wkt` last.
HARMONISED_COLUMNS = ("lot", "section", "plan", "parcel_label", "title_ref", "status", "tenure", "is_strata",
                      "is_road", "is_multipart", "area_m2", "perimeter_m", "stated_area_m2", "locality",
                      "feature_name", "source_feature_id", "source_created", "source_last_updated")

# Working columns of the staged CSVs that are not published.
WORKING_COLUMNS = ("gnaf_locality",)

# Separator of list values (address ids, link methods) in the staged CSVs; lists in the Parquet output.
LIST_SEPARATOR = "|"
