"""Column descriptions and types used by the data dictionary."""

# column -> (type, description)
PARCEL_COLUMNS = {
    "state": ("string", "State or territory code (NSW, VIC, QLD, TAS, ACT, WA, SA, NT)."),
    "source_oid": ("integer", "ObjectID of the parcel in the source service. Unique within the file."),
    "gnaf_legal_parcel_id": ("string", "Parcel key in G-NAF `LEGAL_PARCEL_ID` format: the first candidate key "
                                       "that exists in G-NAF, otherwise the best available candidate."),
    "gnaf_key_matched": ("boolean", "True if `gnaf_legal_parcel_id` exists in G-NAF."),
    "gnaf_address_count": ("integer", "Number of distinct G-NAF addresses linked to the parcel."),
    "gnaf_address_detail_pids": ("list<string>", "G-NAF `ADDRESS_DETAIL_PID`s of the addresses on the parcel "
                                                 "(null if none). Explode and join to G-NAF `ADDRESS_DETAIL`."),
    "gnaf_link_methods": ("list<string>", "How those addresses were linked: `legal_parcel_id` (G-NAF's "
                                          "`LEGAL_PARCEL_ID` equals `gnaf_legal_parcel_id`) and/or `spatial_within` "
                                          "(the address point lies in this parcel, the smallest polygon containing "
                                          "it). Null if none."),
    "geometry_group_id": ("integer", "Parcels with an identical polygon (e.g. stacked strata lots) share this id: "
                                     "the lowest `source_oid` in the group. Equals `source_oid` for most parcels."),
    "geometry_group_size": ("integer", "Number of parcels sharing this exact polygon (1 = unique)."),
    "point_lon": ("number", "Longitude (EPSG:4326) of a point guaranteed to lie inside the parcel."),
    "point_lat": ("number", "Latitude (EPSG:4326) of a point guaranteed to lie inside the parcel."),
    "wkt": ("string", "Parcel boundary as WKT POLYGON or MULTIPOLYGON, EPSG:4326 (lon/lat)."),
}

HARMONISED_COLUMNS = {
    "lot": ("string", "Lot number (ACT: block number)."),
    "section": ("string", "Section number."),
    "plan": ("string", "Plan the lot is on, with its type prefix, e.g. `DP246488`, `PS936577`, `SP12345`."),
    "parcel_label": ("string", "The state's own human-readable parcel identifier, e.g. NSW `1//DP12345`, "
                               r"VIC `1\PS936577`, QLD `4SE1`, TAS `207296/1`, ACT `TUGG/COND/160/32`."),
    "title_ref": ("string", "Certificate of title reference as `volume/folio` (TAS, ACT)."),
    "status": ("string", "`current`, `proposed` or `retired`."),
    "tenure": ("string", "`freehold`, `lease`, `crown`, `council`, `commonwealth` or `other`."),
    "is_strata": ("boolean", "True for strata / volumetric lots (lots in a building or above/below ground)."),
    "is_road": ("boolean", "True for road and footway parcels."),
    "is_multipart": ("boolean", "True if the parcel polygon has more than one part."),
    "area_m2": ("number", "Area of the polygon in m², computed in Australian Albers equal-area (EPSG:3577). "
                          "Comparable across states."),
    "perimeter_m": ("number", "Perimeter of the polygon in metres, computed in EPSG:3577."),
    "stated_area_m2": ("number", "Area stated or measured by the state (survey / title area), in m²."),
    "locality": ("string", "Suburb or locality (upper case): the most common locality of the parcel's G-NAF "
                           "addresses, else the state's own locality field."),
    "feature_name": ("string", "Name of the parcel or feature (e.g. a park, reserve or property name)."),
    "source_feature_id": ("string", "The state's persistent feature id, stable across releases (e.g. NSW "
                                    "`cadid`, VIC `parcel_pfi`)."),
    "source_created": ("date", "Date the state created the parcel record."),
    "source_last_updated": ("date", "Date the state last changed the parcel record."),
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

SUMMARY_COLUMNS = {
    "state": ("string", "State or territory code."),
    "source": ("string", "Source service URL (or local file)."),
    "features_expected": ("integer", "Feature count reported by the source service."),
    "parcels_written": ("integer", "Parcels in the state's parcels file."),
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
