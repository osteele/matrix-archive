
from pathlib import Path
from urllib.parse import urlparse

import click
import requests

import database_connection  # noqa: F401
from matrix_connection import get_download_url
from schema import Message


def download_stem(message, prefer_thumbnails):
    image_url = (message.thumbnail_url if prefer_thumbnails else None) \
        or message.image_url
    return urlparse(image_url).path.lstrip('/')


def run_downloads(messages, download_dir, prefer_thumbnails):
    for msg in messages:
        image_url = (msg.thumbnail_url if prefer_thumbnails else None) or msg.image_url
        res = requests.head(get_download_url(image_url))
        assert res.status_code == 200
        mtype, subtype = res.headers['content-type'].split('/', 2)
        if mtype != 'image':
            print(f"Skipping {image_url}: {res.headers['content-type']}")
            continue

        res = requests.get(get_download_url(image_url))
        assert res.status_code == 200
        filename = (download_dir / download_stem(msg, prefer_thumbnails)
                    ).with_suffix('.' + subtype)
        print('Downloading', image_url, '->', filename)
        with open(filename, 'wb') as fp:
            fp.write(res.content)


@click.command()
@click.option('--thumbnails/--no-thumbnails', default=True)
@click.argument('output', required=False)
def download_images(thumbnails, output):
    """Download thumbnails."""
    noun = 'thumbnails' if thumbnails else 'images'
    download_dir = Path(output or noun)
    messages = [msg for msg in Message.objects
                if msg.content.get('msgtype') == 'm.image']
    download_dir.mkdir(exist_ok=True)
    current_stems = {p.stem for p in download_dir.glob('*')}
    new_messages = [msg for msg in messages
                    if download_stem(msg, thumbnails)
                    not in current_stems]
    skip_count = len(messages) - len(new_messages)
    if skip_count:
        print(f"Skipping {skip_count} already-downloaded {noun}")
    if new_messages:
        print(f"Downloading {len(new_messages)} new {noun}...")
    else:
        print("Nothing to do")
    run_downloads(new_messages, download_dir, prefer_thumbnails=thumbnails)


if __name__ == '__main__':
    download_images()
