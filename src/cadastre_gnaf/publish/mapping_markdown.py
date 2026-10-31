from cadastre_gnaf.constants import HARMONISED_COLUMNS
from cadastre_gnaf.publish.describe_spec import MAX_INLINE_CODES, describe_spec
from cadastre_gnaf.publish.field_map import FIELD_MAP
from cadastre_gnaf.tabular.source_column_name import source_column_name

COMPUTED = {"area_m2", "perimeter_m", "is_multipart"}
OPEN_STATES = ("NSW", "VIC", "QLD", "TAS", "ACT", "WA")


def mapping_markdown(states=OPEN_STATES):
    """Markdown: which published `src_*` column fills each harmonised column per state, then the longer
    code translations (e.g. tenure) as lists."""
    out = ["| Column | " + " | ".join(states) + " |", "|---|" + "---|" * len(states)]
    for col in HARMONISED_COLUMNS:
        if col in COMPUTED:
            cells = ["polygon"] * len(states)
        else:
            cells = [describe_spec(FIELD_MAP.get(st, {}).get(col), source_column_name) or "–" for st in states]
            if col == "locality":
                cells = ["G-NAF" + (f", else {c}" if c != "–" else "") for c in cells]
        out.append(f"| `{col}` | " + " | ".join(c.replace("|", r"\|") for c in cells) + " |")
    for st in states:
        for col, spec in FIELD_MAP.get(st, {}).items():
            if isinstance(spec, tuple) and spec[0] == "map" and len(spec[2]) > MAX_INLINE_CODES:
                codes = "; ".join(f"{k} → {v or 'null'}" for k, v in spec[2].items())
                extra = ", anything else → other" if col == "tenure" else ""
                out += ["", f"**{st} `{col}`** from `{source_column_name(spec[1])}`: {codes}{extra}."]
    return "\n".join(out)
