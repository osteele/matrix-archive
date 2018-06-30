import json
import os
import re
from pathlib import Path

import click
import yaml
from jinja2 import Template
from matrix_client.client import MatrixClient

import database_connection  # noqa: F401
from schema import Message

MATRIX_ROOM_IDS = os.environ['MATRIX_ROOM_IDS'].split(',')

ARCHIVE_FORMATS = ['txt', 'html', 'json', 'yaml']

MATRIX_HOST = os.environ.get('MATRIX_HOST', "https://matrix.org")
get_matrix_download_url = MatrixClient(MATRIX_HOST).api.get_download_url


def encode_message(message):
    data = message._data.copy()
    data.pop('id')
    data['sender'] = re.sub(r'@(.+):.+', r'\1', data['sender'])
    data['timestamp'] = data['timestamp'].isoformat()
    content = data['content']
    if 'url' in content:
        content['url'] = get_matrix_download_url(content['url'])
    return data


def dump_html_archive(data, fp, template_path):
    template = Template(Path(template_path).read_text())
    fp.write(template.render(messages=data))


@click.command()
@click.option('--room-id')
# @click.option('--format', type=click.Choice(ARCHIVE_FORMATS), default='html')
@click.argument('filename')
def export_archive(room_id, filename):
    if not room_id:
        room_id, = MATRIX_ROOM_IDS
    fmt = Path(filename).suffix.lstrip('.')
    if fmt not in ARCHIVE_FORMATS:
        raise click.BadParameter(f"{fmt} is not in {ARCHIVE_FORMATS}")
    messages = Message.objects(room_id=room_id).order_by('timestamp')
    data = map(encode_message, messages)
    print(f"Writing {len(messages)} messages to {filename!r}")
    with open(filename, 'w') as fp:
        if fmt in ('text', 'txt', 'html'):
            template_path = f'templates/default.{fmt}.tpl'
            dump_html_archive(data, fp, template_path=template_path)
        elif fmt == 'json':
            json.dump(list(data), fp, indent=2)
        elif fmt == 'yaml':
            yaml.dump(list(data), fp, default_flow_style=None)


if __name__ == '__main__':
    export_archive()
