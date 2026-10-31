import datetime as dt


def attribution_markdown(rows, built=None):
    """ATTRIBUTION.md text listing every source and its licence."""
    built = built or dt.datetime.now()
    return (
        "# Data sources and licences\n\n"
        + "\n".join(f"- **{r['state']}**: {r['licence']}. Source: {r['source']}" for r in rows)
        + "\n- **G-NAF**: Geoscape Australia, Geocoded National Address File, via data.gov.au "
          "(CC BY 4.0, subject to the Open G-NAF use restriction).\n\n"
          "Cadastral polygons are graphical representations only, not legal boundaries. "
          "Built " + built.isoformat(timespec="minutes") + ".\n")
