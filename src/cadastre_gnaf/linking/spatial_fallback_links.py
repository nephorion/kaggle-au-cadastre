from cadastre_gnaf.linking.spatial_links import spatial_links


def spatial_fallback_links(parcels_csv, address_parcels, points, linked_pids, label="", keep=None):
    """Spatial-join links for addresses not already linked by key (method = 'spatial_within').

    `keep` is passed to spatial_links (parcels allowed to receive addresses).
    """
    todo = set(address_parcels["ADDRESS_DETAIL_PID"]) - set(linked_pids)
    sj = spatial_links(parcels_csv, points[points["ADDRESS_DETAIL_PID"].isin(todo)], label=label, keep=keep)
    sj = sj.merge(address_parcels[["ADDRESS_DETAIL_PID", "LEGAL_PARCEL_ID"]].rename(
        columns={"ADDRESS_DETAIL_PID": "address_detail_pid", "LEGAL_PARCEL_ID": "legal_parcel_id"}),
        on="address_detail_pid", how="left")
    sj["method"] = "spatial_within"
    return sj
