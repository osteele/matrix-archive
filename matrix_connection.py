import os

from matrix_client.client import MatrixClient

_matrix_client = None

MATRIX_USER = os.environ['MATRIX_USER']
MATRIX_PASSWORD = os.environ['MATRIX_PASSWORD']
MATRIX_HOST = os.environ.get('MATRIX_HOST', "https://matrix.org")


def matrix_client():
    global _matrix_client
    if _matrix_client:
        return _matrix_client
    print(f"Signing into {MATRIX_HOST}...")
    client = MatrixClient(MATRIX_HOST)
    client.login_with_password(username=MATRIX_USER,
                               password=MATRIX_PASSWORD)
    _matrix_client = client
    return client
