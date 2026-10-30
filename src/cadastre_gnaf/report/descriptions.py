"""Column descriptions and types used by the data dictionary."""

# column -> (type, description)
PARCEL_COLUMNS = {
    "state": ("string", "State or territory code (NSW, VIC, QLD, TAS, ACT, WA, SA, NT)."),
    "source_oid": ("integer", "ObjectID of the parcel in the source service. Unique within the file; joins to "
                              "`source_oid` in the matching address links file."),
    "gnaf_legal_parcel_id": ("string", "Parcel key in G-NAF `LEGAL_PARCEL_ID` format: the first candidate key "
                                       "that exists in G-NAF, otherwise the best available candidate."),
    "gnaf_key_matched": ("boolean", "True if `gnaf_legal_parcel_id` exists in G-NAF."),
    "gnaf_address_count": ("integer", "Number of distinct G-NAF addresses linked to the parcel."),
    "point_lon": ("number", "Longitude (EPSG:4326) of a point guaranteed to lie inside the parcel."),
    "point_lat": ("number", "Latitude (EPSG:4326) of a point guaranteed to lie inside the parcel."),
    "wkt": ("string", "Parcel boundary as WKT POLYGON or MULTIPOLYGON, EPSG:4326 (lon/lat)."),
}

KEY_COLUMNS = {
    "key_lot_sec_plannum": "Candidate key lot/section/plan number, e.g. `13/31993` or `11/C/3625` "
                           "(G-NAF's documented NSW format).",
    "key_lotidstring": "Candidate key from the source `lotidstring`, e.g. `1//DP12345`.",
    "key_lot_sec_label": "Candidate key lot/section/plan label, e.g. `1//DP12345`.",
    "key_lot_label": "Candidate key lot/plan label, e.g. `1/DP12345`.",
    "key_spi": "Candidate key from the Vicmap Standard Parcel Identifier, e.g. `1TP201500`.",
    "key_lot_plan": "Candidate key lot/plan, e.g. `66/RP139841`.",
    "key_lotplan": "Candidate key from the source `lotplan`, e.g. `66RP139841`.",
    "key_vol_folio": "Candidate key volume/folio without leading zeros, e.g. `158882/1`.",
    "key_vol_folio_raw": "Candidate key volume/folio as published.",
    "key_dist_div_sec_blk": "Candidate key district/division/section/block, e.g. `CANB/BRAD/18/41`.",
    "key_dist_blk": "Candidate key district/block, e.g. `JERV/927`.",
    "key_piparcel_lot": "Candidate key PI parcel/lot, e.g. `S030337/1` (empty on the public geometry-only layer).",
    "key_plant_plan_parcelt_parcel": "Candidate key plan type/plan/parcel type/parcel, e.g. `D/10001/A/14`.",
    "key_dcdbid": "Candidate key from the source `DCDBID`.",
    "key_loc_par_lto": "Candidate key location/parcel/LTO, e.g. `550/3252/`.",
    "key_loc_lto_par": "Candidate key location/LTO/parcel.",
}

LINK_COLUMNS = {
    "address_detail_pid": ("string", "G-NAF address identifier (`ADDRESS_DETAIL.ADDRESS_DETAIL_PID`)."),
    "legal_parcel_id": ("string", "G-NAF `LEGAL_PARCEL_ID` recorded for the address."),
    "source_oid": ("integer", "Parcel `source_oid` in the state's parcels file."),
    "method": ("string", "`legal_parcel_id` (key match) or `spatial_within` (address point inside the parcel "
                                "polygon, for addresses the key did not link)."),
}

SUMMARY_COLUMNS = {
    "state": ("string", "State or territory code."),
    "source": ("string", "Source service URL (or local file)."),
    "features_expected": ("integer", "Feature count reported by the source service."),
    "parcels_written": ("integer", "Rows in the state's parcels file."),
    "parcels_matching_gnaf_key": ("integer", "Parcels whose `gnaf_legal_parcel_id` exists in G-NAF."),
    "gnaf_addresses": ("integer", "G-NAF addresses in the state that carry a legal parcel id."),
    "address_link_rate": ("number", "Share of those G-NAF addresses linked to a parcel."),
    "key_match_by_candidate": ("string", "JSON: matched/total parcels for each candidate key."),
    "licence": ("string", "Licence of the state's source data."),
}

ESRI_TYPES = {
    "esriFieldTypeOID": "integer", "esriFieldTypeInteger": "integer", "esriFieldTypeSmallInteger": "integer",
    "esriFieldTypeBigInteger": "integer", "esriFieldTypeDouble": "number", "esriFieldTypeSingle": "number",
    "esriFieldTypeDate": "date", "esriFieldTypeDateOnly": "date", "esriFieldTypeString": "string",
    "esriFieldTypeGUID": "string", "esriFieldTypeGlobalID": "string",
}
