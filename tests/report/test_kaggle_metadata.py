from cadastre_gnaf.report import kaggle_metadata

FILES = [{"file": "A.csv", "description": "File A"}]
ROWS = [{"file": "A.csv", "column": "n", "type": "number", "description": "n"},
        {"file": "A.csv", "column": "d", "type": "date", "description": "d"},
        {"file": "B.csv", "column": "z", "type": "weird", "description": "z"}]


def test_metadata():
    m = kaggle_metadata("me/x", FILES, ROWS, "# readme")
    assert m["id"] == "me/x" and m["description"] == "# readme"
    assert 6 <= len(m["title"]) <= 50 and 20 <= len(m["subtitle"]) <= 80
    assert m["licenses"] == [{"name": "other"}]
    assert m["resources"] == [{"path": "A.csv", "description": "File A", "schema": {"fields": [
        {"name": "n", "description": "n", "type": "numeric"},
        {"name": "d", "description": "d", "type": "datetime"}]}}]


def test_unknown_type_is_string():
    m = kaggle_metadata("me/x", [{"file": "B.csv", "description": "B"}], ROWS, "")
    assert m["resources"][0]["schema"]["fields"][0]["type"] == "string"
