import re


def source_column_name(name):
    """Published name of a source attribute: `src_` + lower-case snake case (`TENURE_TY` -> `src_tenure_ty`)."""
    snake = re.sub(r"[^0-9a-z]+", "_", name.lower()).strip("_")
    return snake if snake.startswith("src_") else f"src_{snake}"
