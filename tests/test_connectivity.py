import requests
import os

confluence_url = os.environ['CONFLUENCE_URL']


def test_connectivity():
    """
    Test (ssl) connectivity to confluence url
    """
    r = requests.get(confluence_url)
    assert 200 <= r.status_code <= 399
