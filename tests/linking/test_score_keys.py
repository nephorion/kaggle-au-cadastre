import numpy as np
import pandas as pd

from cadastre_gnaf.linking import score_keys


def test_counts_matches_and_sorts_best_first():
    kd = pd.DataFrame({"a": ["X", "Y", np.nan], "b": ["P", "Q", "R"]}, index=["1", "2", "3"])
    assert score_keys(kd, {"P", "Q", "X"}) == [("b", 2, 3), ("a", 1, 2)]


def test_ties_keep_column_order():
    kd = pd.DataFrame({"a": ["X"], "b": ["X"]})
    assert [k for k, _, _ in score_keys(kd, set())] == ["a", "b"]
