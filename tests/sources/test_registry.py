from cadastre_gnaf.constants import DEFAULT_STATES
from cadastre_gnaf.sources import SOURCES


def test_every_default_state_has_a_source():
    assert set(SOURCES) == set(DEFAULT_STATES)


def test_open_states_have_https_urls():
    for st in ("NSW", "VIC", "QLD", "TAS", "ACT", "WA"):
        assert SOURCES[st].url.startswith("https://"), st


def test_licensed_states_have_no_url():
    assert SOURCES["SA"].url is None and SOURCES["NT"].url is None


def test_key_builders_accept_empty_attributes():
    for st, src in SOURCES.items():
        keys = src.keys({})
        assert keys and all(k.startswith("key_") for k in keys), st
        assert src.licence, st
