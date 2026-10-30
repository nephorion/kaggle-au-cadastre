from cadastre_gnaf.gnaf.format_address import format_address
from cadastre_gnaf.gnaf.read_address_points import read_address_points
from cadastre_gnaf.gnaf.read_table import read_table

DETAIL_COLUMNS = {
    "ADDRESS_DETAIL_PID", "DATE_RETIRED", "BUILDING_NAME", "LOT_NUMBER_PREFIX", "LOT_NUMBER", "LOT_NUMBER_SUFFIX",
    "FLAT_TYPE_CODE", "FLAT_NUMBER_PREFIX", "FLAT_NUMBER", "FLAT_NUMBER_SUFFIX", "LEVEL_TYPE_CODE",
    "LEVEL_NUMBER_PREFIX", "LEVEL_NUMBER", "LEVEL_NUMBER_SUFFIX", "NUMBER_FIRST_PREFIX", "NUMBER_FIRST",
    "NUMBER_FIRST_SUFFIX", "NUMBER_LAST_PREFIX", "NUMBER_LAST", "NUMBER_LAST_SUFFIX", "STREET_LOCALITY_PID",
    "LOCALITY_PID", "POSTCODE",
}


def read_addresses(source, state, pids=None):
    """Live G-NAF addresses of a state as address_* columns (full address, parts and default geocode).

    `pids` limits the result to those ADDRESS_DETAIL_PIDs.
    """
    d = read_table(source, state, "ADDRESS_DETAIL", DETAIL_COLUMNS)
    if pids is not None:
        d = d[d["ADDRESS_DETAIL_PID"].isin(set(pids))]
    streets = read_table(source, state, "STREET_LOCALITY", {"STREET_LOCALITY_PID", "STREET_NAME", "STREET_TYPE_CODE",
                                                            "STREET_SUFFIX_CODE", "DATE_RETIRED"})
    localities = read_table(source, state, "LOCALITY", {"LOCALITY_PID", "LOCALITY_NAME", "DATE_RETIRED"})
    d = (d.merge(streets.drop_duplicates("STREET_LOCALITY_PID"), on="STREET_LOCALITY_PID", how="left")
          .merge(localities.drop_duplicates("LOCALITY_PID"), on="LOCALITY_PID", how="left"))
    out = format_address(d, state)
    out.insert(0, "address_detail_pid", d["ADDRESS_DETAIL_PID"])
    points = read_address_points(source, state).drop_duplicates("ADDRESS_DETAIL_PID")
    points = points.rename(columns={"ADDRESS_DETAIL_PID": "address_detail_pid", "LONGITUDE": "address_lon",
                                    "LATITUDE": "address_lat"})
    return out.merge(points[["address_detail_pid", "address_lon", "address_lat"]], on="address_detail_pid",
                     how="left").reset_index(drop=True)
