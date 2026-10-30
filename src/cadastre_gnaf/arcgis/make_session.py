import requests

from cadastre_gnaf.constants import USER_AGENT


def make_session():
    """HTTP session with a polite, identifiable User-Agent."""
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session
