import pandas as pd

from cadastre_gnaf.gnaf import open_gnaf, read_addresses
from cadastre_gnaf.linking.write_parcel_addresses import write_parcel_addresses
from cadastre_gnaf.storage import links_path, parcel_addresses_path, parcels_path


def run_parcel_addresses(config, session, gnaf=None):
    """Write <STATE>_parcels_with_addresses for every state that has a parcels and a links file."""
    gnaf = gnaf or open_gnaf(config, session)
    for st in config.states:
        parcels, links_csv = parcels_path(config, st), links_path(config, st)
        if not (parcels.exists() and links_csv.exists()):
            continue
        try:
            links = pd.read_csv(links_csv, dtype=str, keep_default_na=False)
            addresses = read_addresses(gnaf, st, links["address_detail_pid"])
            out = parcel_addresses_path(config, st)
            rows = write_parcel_addresses(parcels, links, addresses, out, config.compression)
            print(f"[{st}] {rows:,} parcel/address rows -> {out.name}")
        except Exception as e:
            print(f"[{st}] parcels with addresses FAILED: {e!r}")
