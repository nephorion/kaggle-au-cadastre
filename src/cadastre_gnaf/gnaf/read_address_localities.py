from cadastre_gnaf.gnaf.read_table import read_table


def read_address_localities(source, state):
    """Live addresses with the name of their locality: ADDRESS_DETAIL_PID, LOCALITY_NAME."""
    d = read_table(source, state, "ADDRESS_DETAIL", {"ADDRESS_DETAIL_PID", "LOCALITY_PID", "DATE_RETIRED"})
    loc = read_table(source, state, "LOCALITY", {"LOCALITY_PID", "LOCALITY_NAME", "DATE_RETIRED"})
    d = d.merge(loc.drop_duplicates("LOCALITY_PID"), on="LOCALITY_PID", how="left")
    return d[["ADDRESS_DETAIL_PID", "LOCALITY_NAME"]].fillna("")
