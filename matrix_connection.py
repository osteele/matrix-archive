import os
from urllib.parse import urlparse

from matrix_client.client import MatrixClient

MATRIX_USER = os.environ['MATRIX_USER']
MATRIX_PASSWORD = os.environ['MATRIX_PASSWORD']
MATRIX_HOST = os.environ.get('MATRIX_HOST', "https://matrix.org")

_client = None
_download_url_resolvers = dict()


def matrix_client():
    global _client
    if _client:
        return _client
    print(f"Signing into {MATRIX_HOST}...")
    client = MatrixClient(MATRIX_HOST)
    client.login_with_password(username=MATRIX_USER,
                               password=MATRIX_PASSWORD)
    _client = client
    return client


def get_download_url(url):
    u = urlparse(url)
    assert u.scheme == 'mxc'
    host = u.netloc
    resolvers = _download_url_resolvers
    resolver = resolvers.get(host) or MatrixClient(host).api.get_download_url
    resolvers[host] = resolver
    return 'https://' + resolver(url)


get_matrix_download_url = MatrixClient(MATRIX_HOST).api.get_download_url
