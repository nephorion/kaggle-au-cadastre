import pytest

from cadastre_gnaf.publish import describe_spec
from cadastre_gnaf.publish.field_map import FIELD_MAP


@pytest.mark.parametrize(("spec", "text"), [
    (None, ""),
    ("lotnumber", "`lotnumber`"),
    (("const", "lease"), "always `lease`"),
    (("map", "s", {"A": "current", "G": ""}), "`s` (A → current, G → null)"),
    (("prefix", "DP", "n"), "`DP` + `n`"),
    (("join", "/", ["V", "F"]), "`V` + `/` + `F`"),
    (("replace", "vf", ":", "/"), "`vf` with `:` → `/`"),
    (("first", ["a", "b"]), "`a`, else `b`"),
    (("int", "ID"), "`ID`"),
    (("date", "d"), "`d`"),
    (("area", "a", "u"), "`a` in `u` units, as m²"),
    (("area", "a", None), "`a`, as m²"),
    (("match", "r", "^Y$"), "`r` matches `^Y$`"),
    (("present", "p"), "`p` is present"),
])
def test_describes(spec, text):
    assert describe_spec(spec) == text


def test_every_spec_in_the_field_map_is_describable():
    for fields in FIELD_MAP.values():
        for spec in fields.values():
            assert describe_spec(spec)


def test_unknown_spec():
    with pytest.raises(ValueError):
        describe_spec(("nope",))
