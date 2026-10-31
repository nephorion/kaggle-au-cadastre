from cadastre_gnaf.constants import HARMONISED_COLUMNS
from cadastre_gnaf.publish import mapping_markdown


def test_one_row_per_harmonised_column():
    md = mapping_markdown()
    assert md.startswith("| Column | NSW | VIC | QLD | TAS | ACT | WA |")
    for col in HARMONISED_COLUMNS:
        assert f"| `{col}` |" in md


def test_uses_published_names_and_lists_long_code_maps():
    md = mapping_markdown()
    assert "| `lot` | `src_lotnumber` | `src_parcel_lot_number` | `src_lot` | – | `src_block_number` | – |" in md
    assert "| `area_m2` | polygon | polygon |" in md
    assert "`src_tenure`, translated (codes below)" in md
    assert "**QLD `tenure`** from `src_tenure`: Freehold → freehold;" in md and "anything else → other" in md
    assert "| `locality` | G-NAF | G-NAF | G-NAF, else `src_locality` |" in md


def test_pipes_escaped():
    assert r"`Road\|Footway`" in mapping_markdown()
