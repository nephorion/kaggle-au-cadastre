def key_names(key_builder):
    """Candidate key column names produced by a state's key builder."""
    return list(key_builder({}).keys())
