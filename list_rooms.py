import re

import click

from matrix_connection import matrix_client
from tabulate import tabulate


@click.command()
@click.argument('pattern', required=False, type=str)
def list_rooms(pattern):
    """List room ids and keys."""
    rooms = matrix_client().get_rooms()
    data = [(rid, room.display_name)
            for rid, room in rooms.items()]
    if pattern:
        data = [(rid, name) for rid, name in data
                if re.search(pattern.strip('/'), name)]
    print(tabulate(data, headers=['Room ID', 'Display Name']))


if __name__ == '__main__':
    list_rooms()
