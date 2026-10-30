from cadastre_gnaf.linking.spatial_links import spatial_links


def spatial_fallback_links(parcels_csv, address_parcels, points, linked_pids, label=""):
    """Spatial-join links for addresses not already linked by key (method = 'spatial_within')."""
    todo = set(address_parcels["ADDRESS_DETAIL_PID"]) - set(linked_pids)
    sj = spatial_links(parcels_csv, points[points["ADDRESS_DETAIL_PID"].isin(todo)], label=label)
    sj = sj.merge(address_parcels[["ADDRESS_DETAIL_PID", "LEGAL_PARCEL_ID"]].rename(
        columns={"ADDRESS_DETAIL_PID": "address_detail_pid", "LEGAL_PARCEL_ID": "legal_parcel_id"}),
        on="address_detail_pid", how="left")
    sj["method"] = "spatial_within"
    return sj
