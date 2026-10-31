from cadastre_gnaf.constants import GNAF_PACKAGE_API, GNAF_PACKAGE_ID


def latest_gnaf_zip_url(session):
    """URL of the newest GDA2020 G-NAF zip listed on data.gov.au."""
    res = session.get(GNAF_PACKAGE_API, params={"id": GNAF_PACKAGE_ID}, timeout=60).json()["result"]["resources"]
    cands = [r for r in res if str(r.get("url", "")).lower().endswith(".zip")
             and "gda2020" in (str(r.get("name", "")) + str(r.get("url", ""))).lower()]
    if not cands:
        raise RuntimeError("No GDA2020 G-NAF zip found on data.gov.au; pass --gnaf-zip-url.")
    cands.sort(key=lambda r: r.get("created") or r.get("last_modified") or "", reverse=True)
    print("G-NAF release:", cands[0].get("name"))
    return cands[0]["url"]
