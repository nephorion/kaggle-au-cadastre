import dataclasses

import pytest

from cadastre_gnaf.sources import Source


def test_default_where_clause():
    assert Source(url="u", keys=dict, licence="l").where == "1=1"


def test_is_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        Source(url="u", keys=dict, licence="l").url = "x"
