import numpy as np
import pandas as pd

from cadastre_gnaf.linking import fallback_keys


def test_first_non_empty_candidate():
    kd = pd.DataFrame({"a": [np.nan, "A2"], "b": ["B1", "B2"]}, index=["1", "2"])
    chosen, matched = fallback_keys(kd)
    assert chosen.tolist() == ["B1", "A2"]
    assert not matched.any()


def test_no_candidate_columns():
    chosen, matched = fallback_keys(pd.DataFrame(index=["1", "2"]))
    assert chosen.isna().all() and len(chosen) == 2
    assert not matched.any()
