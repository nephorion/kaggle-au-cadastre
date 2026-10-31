def parcel_localities(links, address_localities):
    """source_oid -> the most common locality among the parcel's linked addresses (ties: alphabetical)."""
    m = links[["source_oid", "address_detail_pid"]].drop_duplicates().merge(
        address_localities, left_on="address_detail_pid", right_on="ADDRESS_DETAIL_PID")
    m = m[m["LOCALITY_NAME"] != ""]
    n = m.groupby(["source_oid", "LOCALITY_NAME"]).size().reset_index(name="n")
    n = n.sort_values(["source_oid", "n", "LOCALITY_NAME"], ascending=[True, False, True])
    return n.drop_duplicates("source_oid").set_index("source_oid")["LOCALITY_NAME"]
