import threading
import time

import pytest

from cadastre_gnaf.download import fetch_in_order


def test_yields_ranges_in_order():
    out = list(fetch_in_order(lambda lo, hi: [lo], 1, 10, 3, workers=2))
    assert out == [(1, 4, [1]), (4, 7, [4]), (7, 10, [7]), (10, 13, [10])]


def test_empty_when_start_after_stop():
    assert list(fetch_in_order(lambda lo, hi: [lo], 5, 4, 1, workers=2)) == []


def test_slow_head_does_not_block_other_workers():
    release = threading.Event()
    done = []

    def fetch(lo, hi):
        if lo == 0:
            release.wait(5)                              # head of the queue is stuck...
        done.append(lo)
        return [lo]

    gen = fetch_in_order(fetch, 0, 9, 1, workers=2)
    t = threading.Thread(target=lambda: next(gen))
    t.start()
    deadline = time.time() + 5
    while len(done) < 9 and time.time() < deadline:     # ...while the other worker drains the rest
        time.sleep(0.01)
    assert sorted(done) == list(range(1, 10))
    release.set()
    t.join()
    assert [lo for lo, _, _ in gen] == list(range(1, 10))


def test_skips_gap_after_a_window_of_empty_ranges():
    asked = []

    def find_next(at_least):
        asked.append(at_least)
        return 1000

    fetched = []

    def fetch(lo, hi):
        fetched.append(lo)
        return [lo] if lo in (0, 1000) else []

    out = list(fetch_in_order(fetch, 0, 1000, 1, workers=1, find_next=find_next))
    assert out[0] == (0, 1, [0]) and out[-1] == (1000, 1001, [1000])
    assert asked and len(fetched) < 100


def test_stops_when_no_more_oids():
    out = list(fetch_in_order(lambda lo, hi: [], 0, 10_000, 1, workers=1, find_next=lambda at_least: None))
    assert len(out) < 100


def test_errors_propagate():
    def fetch(lo, hi):
        if lo == 2:
            raise RuntimeError("boom")
        return [lo]

    gen = fetch_in_order(fetch, 0, 5, 1, workers=2)
    assert [next(gen)[0], next(gen)[0]] == [0, 1]
    with pytest.raises(RuntimeError, match="boom"):
        next(gen)
