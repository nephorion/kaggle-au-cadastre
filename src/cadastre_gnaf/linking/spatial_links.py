import pandas as pd

CSV_CHUNK_ROWS = 500_000


def spatial_links(parcels_csv, points, chunk=500_000, label="", keep=None):
    """Point-in-polygon join of G-NAF default geocodes to parcel polygons (needs geopandas).

    Each address goes to the smallest polygon that contains it. `keep` (a set of source_oids, as str)
    limits the join to those parcels, e.g. one representative per stack of identical polygons.
    """
    import geopandas as gpd
    import shapely
    from shapely import from_wkt, make_valid

    parts = []
    for c in pd.read_csv(parcels_csv, usecols=["source_oid", "wkt"], dtype={"wkt": str}, chunksize=CSV_CHUNK_ROWS):
        c = c[c["wkt"].fillna("") != ""]
        if keep is not None:
            c = c[c["source_oid"].astype(str).isin(keep)]
        parts.append(gpd.GeoDataFrame(c[["source_oid"]], geometry=from_wkt(c["wkt"].values), crs=4326))
    polys = pd.concat(parts, ignore_index=True)
    polys = polys[polys.geometry.notna()].copy()
    bad = ~polys.is_valid
    polys.loc[bad, "geometry"] = make_valid(polys.loc[bad, "geometry"].values)
    polys["poly_area"] = shapely.area(polys.geometry.values)      # degrees², only used to rank overlaps
    out = []
    for i in range(0, len(points), chunk):
        p = points.iloc[i:i + chunk]
        g = gpd.GeoDataFrame(p[["ADDRESS_DETAIL_PID"]],
                             geometry=gpd.points_from_xy(p["LONGITUDE"], p["LATITUDE"]), crs=4326)
        j = gpd.sjoin(g, polys, predicate="within", how="inner")
        j = j.sort_values(["ADDRESS_DETAIL_PID", "poly_area", "source_oid"]).drop_duplicates("ADDRESS_DETAIL_PID")
        out.append(pd.DataFrame({"address_detail_pid": j["ADDRESS_DETAIL_PID"].values,
                                 "source_oid": j["source_oid"].values}))
        print(f"\r  [{label}] spatial join {min(i + chunk, len(points)):,}/{len(points):,} points", end="", flush=True)
    print()
    if not out:
        return pd.DataFrame(columns=["address_detail_pid", "source_oid"])
    return pd.concat(out, ignore_index=True).drop_duplicates("address_detail_pid", ignore_index=True)
