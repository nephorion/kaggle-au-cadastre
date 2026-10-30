import pandas as pd

CSV_CHUNK_ROWS = 500_000


def spatial_links(parcels_csv, points, chunk=500_000, label=""):
    """Point-in-polygon join of G-NAF default geocodes to parcel polygons (needs geopandas)."""
    import geopandas as gpd
    from shapely import from_wkt, make_valid

    parts = []
    for c in pd.read_csv(parcels_csv, usecols=["source_oid", "wkt"], dtype={"wkt": str}, chunksize=CSV_CHUNK_ROWS):
        c = c[c["wkt"].fillna("") != ""]
        parts.append(gpd.GeoDataFrame(c[["source_oid"]], geometry=from_wkt(c["wkt"].values), crs=4326))
    polys = pd.concat(parts, ignore_index=True)
    polys = polys[polys.geometry.notna()].copy()
    bad = ~polys.is_valid
    polys.loc[bad, "geometry"] = make_valid(polys.loc[bad, "geometry"].values)
    out = []
    for i in range(0, len(points), chunk):
        p = points.iloc[i:i + chunk]
        g = gpd.GeoDataFrame(p[["ADDRESS_DETAIL_PID"]],
                             geometry=gpd.points_from_xy(p["LONGITUDE"], p["LATITUDE"]), crs=4326)
        j = gpd.sjoin(g, polys, predicate="within", how="inner")
        out.append(pd.DataFrame({"address_detail_pid": j["ADDRESS_DETAIL_PID"].values,
                                 "source_oid": j["source_oid"].values}))
        print(f"\r  [{label}] spatial join {min(i + chunk, len(points)):,}/{len(points):,} points", end="", flush=True)
    print()
    if not out:
        return pd.DataFrame(columns=["address_detail_pid", "source_oid"])
    # a parcel repeated in the CSV (e.g. after a resumed download) would otherwise duplicate links
    return pd.concat(out, ignore_index=True).drop_duplicates(ignore_index=True)
