from cadastre_gnaf.geometry import esri_to_wkt


def features_to_items(features, decimals=6):
    """Esri JSON features -> [(attrs, wkt, lon, lat)]."""
    items = []
    for f in features:
        wkt, lon, lat = esri_to_wkt(f.get("geometry"), decimals)
        items.append((f.get("attributes", {}), wkt, lon, lat))
    return items
