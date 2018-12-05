import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import click
import yaml
from jinja2 import Template

import database_connection  # noqa: F401
from matrix_connection import get_download_url
from schema import Message

MATRIX_ROOM_IDS = os.environ['MATRIX_ROOM_IDS'].split(',')

ARCHIVE_FORMATS = ['txt', 'html', 'json', 'yaml']


def encode_message(message):
    data = message._data.copy()
    data.pop('id')
    data['sender'] = re.sub(r'@(.+):.+', r'\1', data['sender'])
    data['timestamp'] = data['timestamp'].isoformat()
    content = data['content']
    if 'url' in content:
        content['url'] = get_download_url(content['url'])
    return data


def replace_by_local_image(data):
    data = data.copy()
    content = data['content']
    if content.get('msgtype') == 'm.image':
        url, mimetype = content['url'], content['info']['mimetype']
        if 'thumbnail_url' in content['info']:
            url, mimetype = content['info']['thumbnail_url'], content['info']['thumbnail_info']['mimetype']
        _, subtype = mimetype.split('/', 2)
        url = urlparse(url)
        content['url'] = 'thumbnails/' + url.path.strip('/') + '.' + subtype
    return data


def dump_html_archive(data, fp, template_path):
    template = Template(Path(template_path).read_text())
    fp.write(template.render(messages=data))


@click.command()
@click.option('--room-id')
@click.option('--local-images/--no-local-images', default=True)
@click.argument('filename', default='archive.html')
def export_archive(room_id, local_images, filename):
    if room_id and not re.match(r'!.+:matrix.org', room_id):
        from matrix_connection import matrix_client
        rooms = matrix_client().get_rooms()
        room_id = next(id for id, room in rooms.items() if room_id in room.display_name)
    if not room_id:
        room_id, *_ = MATRIX_ROOM_IDS
    fmt = Path(filename).suffix.lstrip('.')
    if fmt not in ARCHIVE_FORMATS:
        raise click.BadParameter(f"{fmt} is not in {ARCHIVE_FORMATS}")
    messages = Message.objects(room_id=room_id).order_by('timestamp')
    data = map(encode_message, messages)
    print(f"Writing {len(messages)} messages to {filename!r}")
    with open(filename, 'w') as fp:
        if fmt in ('text', 'txt', 'html'):
            if local_images:
                data = map(replace_by_local_image, data)
            template_path = f'templates/default.{fmt}.tpl'
            dump_html_archive(data, fp, template_path=template_path)
        elif fmt == 'json':
            json.dump(list(data), fp, indent=2)
        elif fmt == 'yaml':
            yaml.dump(list(data), fp, default_flow_style=None)


if __name__ == '__main__':
    export_archive()
