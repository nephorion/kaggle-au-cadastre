from cadastre_gnaf.report import kaggle_metadata

FILES = [{"file": "A.csv", "description": "File A"}]
ROWS = [{"file": "A.csv", "column": "n", "type": "number", "description": "n"},
        {"file": "A.csv", "column": "d", "type": "date", "description": "d"},
        {"file": "B.csv", "column": "z", "type": "weird", "description": "z"}]


def test_metadata():
    m = kaggle_metadata("me/x", FILES, ROWS, "# readme", "Sources: x")
    assert m["id"] == "me/x" and m["description"] == "# readme"
    assert 6 <= len(m["title"]) <= 50 and 20 <= len(m["subtitle"]) <= 80
    assert m["licenses"] == [{"name": "other"}]
    assert m["userSpecifiedSources"] == "Sources: x" and m["expectedUpdateFrequency"] == "quarterly"
    assert m["resources"][0] == {"path": "A.csv", "description": "File A", "schema": {"fields": [
        {"name": "n", "description": "n", "type": "numeric"},
        {"name": "d", "description": "d", "type": "datetime"}]}}


def test_documentation_files_are_described():
    resources = kaggle_metadata("me/x", FILES, ROWS, "")["resources"]
    assert [r["path"] for r in resources[1:]] == ["README.md", "ATTRIBUTION.md", "data_dictionary.md",
                                                  "data_dictionary.csv"]
    assert all(r["description"] for r in resources)
    dd = resources[-1]["schema"]["fields"]
    assert [f["name"] for f in dd] == ["file", "column", "type", "description", "example"]
    assert all(f["description"] for f in dd)


def test_unknown_type_is_string():
    m = kaggle_metadata("me/x", [{"file": "B.csv", "description": "B"}], ROWS, "")
    assert m["resources"][0]["schema"]["fields"][0]["type"] == "string"


def test_csv_twin_reuses_the_parquet_schema():
    files = FILES + [{"file": "T.csv", "description": "T (CSV)", "same_as": "T.parquet"}]
    rows = ROWS + [{"file": "T.parquet", "column": "ids", "type": "list<string>", "description": "ids"}]
    m = kaggle_metadata("me/x", files, rows, "")
    assert m["resources"][1]["schema"]["fields"] == [{"name": "ids", "description": "ids", "type": "string"}]
