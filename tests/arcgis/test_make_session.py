import requests

from cadastre_gnaf.arcgis import make_session
from cadastre_gnaf.constants import USER_AGENT


def test_session_has_user_agent():
    s = make_session()
    assert isinstance(s, requests.Session)
    assert s.headers["User-Agent"] == USER_AGENT
