from cadastre_gnaf.report.kaggle_readme_markdown import SUBTITLE, TITLE

# dictionary type -> Kaggle column type
KAGGLE_TYPES = {"integer": "integer", "number": "numeric", "boolean": "boolean", "date": "datetime",
                "string": "string", "list<string>": "string"}
KEYWORDS = ["australia", "geospatial analysis", "real estate", "housing", "government"]
UPDATE_FREQUENCY = "quarterly"                          # G-NAF is released quarterly

# Documentation files in the dataset, described so every file on Kaggle has a description.
DOC_FILES = [
    {"path": "README.md", "description": "This dataset description: contents, coverage, method and examples"},
    {"path": "ATTRIBUTION.md", "description": "Source services and licences of each state's data"},
    {"path": "data_dictionary.md", "description": "Every column of every file: type, description, example"},
    {"path": "data_dictionary.csv", "description": "The data dictionary as a table, one row per file and column",
     "schema": {"fields": [
         {"name": "file", "description": "File the column belongs to.", "type": "string"},
         {"name": "column", "description": "Column name.", "type": "string"},
         {"name": "type", "description": "Column type (string, integer, number, boolean, date, list<string>).",
          "type": "string"},
         {"name": "description", "description": "What the column holds.", "type": "string"},
         {"name": "example", "description": "An example value from the file.", "type": "string"}]}},
]


def kaggle_metadata(kaggle_id, files, rows, readme, sources=""):
    """dataset-metadata.json content for `kaggle datasets create`, with per-column descriptions.

    `sources` is the provenance text shown in Kaggle's "Sources" field.
    """
    return {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "id": kaggle_id,
        "licenses": [{"name": "other"}],                 # mixed state licences, listed in the description
        "keywords": KEYWORDS,
        "description": readme,
        "userSpecifiedSources": sources,
        "expectedUpdateFrequency": UPDATE_FREQUENCY,
        "resources": [
            {"path": f["file"], "description": f["description"],
             "schema": {"fields": [{"name": r["column"], "description": r["description"],
                                    "type": KAGGLE_TYPES.get(r["type"], "string")}
                                   for r in rows if r["file"] == f.get("same_as", f["file"])]}}
            for f in files] + DOC_FILES,
    }
