"""How each state's source attributes fill the harmonised columns.

A spec is one of:
  "name"                         the source column as is
  ("const", value)               the same value for every parcel
  ("map", col, {raw: value})     translate codes; unlisted non-empty values become "other" for tenure, else null
  ("prefix", text, col)          text + value, where the value is present
  ("replace", col, old, new)     the value with `old` replaced by `new`
  ("join", sep, [cols])          values joined with sep, only when all are present
  ("first", [specs])             first spec that gives a value
  ("int", col)                   numeric text as a whole number ("17253.0" -> "17253")
  ("date", col)                  ISO date; far-future "still current" sentinels (year >= 2999) become null
  ("area", col, unit_col)        area in m²; units from unit_col or from the text itself (m², hectares)
  ("match", col, regex)          True if the value matches, False if it does not, null if empty
  ("present", col)               True if the value is present, else False
Columns not listed for a state are null. area_m2, perimeter_m and is_multipart are computed from the
geometry for every state, and locality comes from G-NAF first.
"""

QLD_TENURE = {
    "Freehold": "freehold", "Lands Lease": "lease", "Mines Tenure": "lease",
    "Reserve": "crown", "State Land": "crown", "National Park": "crown", "State Forest": "crown",
    "Timber Reserve": "crown", "Water Resource": "crown", "Railway": "crown", "Housing Land": "crown",
    "Port and Harbours Boards": "crown", "Industrial Estates": "crown", "Commonwealth Acquisition": "commonwealth",
}
TAS_TENURE = {
    "Freehold Title": "freehold", "Horizontal Strata": "freehold", "Vertical Strata": "freehold",
    "Body Corporate": "freehold", "Share Title": "freehold", "Vertical Subdivision": "freehold",
    "Crown Land": "crown", "Tidal Crown Land": "crown", "Marine Crown Land": "crown",
    "Council": "council", "Commonwealth of Australia": "commonwealth", "Unknown": "", "Not Applicable": "",
}

FIELD_MAP = {
    "NSW": {
        "lot": "lotnumber", "section": "sectionnumber", "plan": "planlabel", "parcel_label": "lotidstring",
        "status": ("const", "current"),
        "stated_area_m2": ("area", "planlotarea", "planlotareaunits"),
        "source_feature_id": "cadid", "source_created": ("date", "createdate"),
        "source_last_updated": ("date", "lastupdate"),
    },
    "VIC": {
        "lot": "parcel_lot_number", "section": "parcel_sec", "plan": "parcel_plan_number",
        "parcel_label": "parcel_spi",
        "status": ("map", "parcel_status", {"A": "current", "P": "proposed"}),
        "tenure": ("map", "parcel_crown_status", {"C": "crown", "G": ""}),
        "is_road": ("match", "parcel_road", r"^Y$"),
        "source_feature_id": "parcel_pfi", "source_created": ("date", "parcel_pfi_created"),
        "source_last_updated": ("date", "parcel_ufi_created"),
    },
    "QLD": {
        "lot": "lot", "plan": "plan", "parcel_label": "lotplan",
        "status": ("map", "parcel_state", {"Created": "current", "Existing": "current"}),
        "tenure": ("map", "tenure", QLD_TENURE),
        "is_strata": ("match", "is_volumetric", r"^Yes$"),
        "stated_area_m2": ("area", "statedarea", "statedareaunit"),
        "locality": "locality", "feature_name": "feat_name",
        "source_feature_id": "uniqueid", "source_last_updated": ("date", "last_edited_date"),
    },
    "TAS": {
        "parcel_label": ("join", "/", ["VOLUME", "FOLIO"]), "title_ref": ("join", "/", ["VOLUME", "FOLIO"]),
        "status": ("const", "current"),
        "tenure": ("map", "TENURE_TY", TAS_TENURE),
        "is_strata": ("match", "STRATA_LEV", r"^(?!Not Applicable$)"),
        "is_road": ("match", "CAD_TYPE2", r"Road|Footway"),
        "stated_area_m2": ("area", "MEAS_AREA", None),
        "feature_name": ("first", ["FEAT_NAME", "PROP_NAME"]),
        "source_feature_id": "CID",
    },
    "ACT": {
        "lot": "BLOCK_NUMBER", "section": "SECTION_NUMBER", "plan": ("prefix", "DP", "DEPOSITED_PLAN_NO"),
        "parcel_label": ("join", "/", ["DISTRICT_SHORT", "DIVISION_SHORT", "SECTION_NUMBER", "BLOCK_NUMBER"]),
        "title_ref": ("replace", "VOLUME_FOLIO", ":", "/"),
        "status": ("map", "CURRENT_LIFECYCLE_STAGE",
                   {"REGISTERED": "current", "APPROVED": "proposed", "PROPOSED": "proposed", "RETIRED": "retired"}),
        "tenure": ("const", "lease"),
        "is_strata": ("present", "STRATUM_DATUM_ID"),
        "stated_area_m2": ("area", "BLOCK_LEASED_AREA", None),
        "locality": "DIVISION_NAME",
        "source_feature_id": ("int", "ID"), "source_last_updated": ("date", "LAST_UPDATE"),
    },
    "WA": {},
    "SA": {},
    "NT": {},
}

# Source columns left out of the published files: they repeat source_oid (the layer's ObjectID) or are
# areas/lengths computed by each service in its own projection (replaced by area_m2 / perimeter_m).
DROPPED_SOURCE_COLUMNS = frozenset({"objectid", "fid", "shape__area", "shape__length", "shape_area", "shape_length",
                                    "shape.starea()", "shape.stlength()"})
