import datetime as dt

from cadastre_gnaf.report import dictionary_markdown

ROWS = [{"file": "A.csv", "column": "x", "type": "string", "description": "a|b", "example": "1\n2"},
        {"file": "A.csv", "column": "y", "type": "integer", "description": "y", "example": ""},
        {"file": "B.csv", "column": "z", "type": "number", "description": "z", "example": "1.5"}]
FILES = [{"file": "A.csv", "description": "File A", "rows": 1234}]


def test_one_table_per_file():
    md = dictionary_markdown(ROWS, FILES, built=dt.datetime(2026, 10, 30, 9, 0))
    assert md.startswith("# Data dictionary\n")
    assert "## `A.csv`\n\nFile A. 1,234 rows.\n\n| Column | Type | Description | Example |" in md
    assert "| `x` | string | a\\|b | `1 2` |" in md
    assert "| `y` | integer | y |  |" in md
    assert "## `B.csv`\n\n| Column" in md
    assert md.endswith("Generated 2026-10-30T09:00.\n")
