import numpy as np
import pandas as pd

from cadastre_gnaf.linking import choose_keys

KD = pd.DataFrame({"a": ["A1", "A2", np.nan, np.nan],
                   "b": ["B1", "B2", "B3", np.nan]}, index=["1", "2", "3", "4"])


def test_first_matching_candidate_in_rank_order():
    chosen, matched = choose_keys(KD, ["b", "a"], {"A1", "B1", "A2"})
    assert chosen["1"] == "B1"                         # both match, b ranked first
    assert chosen["2"] == "A2"                         # only a matches
    assert matched.tolist() == [True, True, False, False]


def test_unmatched_fall_back_to_best_ranked_non_empty():
    chosen, matched = choose_keys(KD, ["a", "b"], set())
    assert chosen.tolist()[:3] == ["A1", "A2", "B3"]
    assert pd.isna(chosen["4"])
    assert not matched.any()
