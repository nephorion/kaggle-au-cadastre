from cadastre_gnaf.report.kaggle_readme_markdown import SUBTITLE, TITLE

# dictionary type -> Kaggle column type
KAGGLE_TYPES = {"integer": "integer", "number": "numeric", "boolean": "boolean", "date": "datetime",
                "string": "string", "list<string>": "string"}
KEYWORDS = ["australia", "geospatial analysis", "real estate", "housing", "government"]


def kaggle_metadata(kaggle_id, files, rows, readme):
    """dataset-metadata.json content for `kaggle datasets create`, with per-column descriptions."""
    return {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "id": kaggle_id,
        "licenses": [{"name": "other"}],                 # mixed state licences, listed in the description
        "keywords": KEYWORDS,
        "description": readme,
        "resources": [
            {"path": f["file"], "description": f["description"],
             "schema": {"fields": [{"name": r["column"], "description": r["description"],
                                    "type": KAGGLE_TYPES.get(r["type"], "string")}
                                   for r in rows if r["file"] == f.get("same_as", f["file"])]}}
            for f in files],
    }
