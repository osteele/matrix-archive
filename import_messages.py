import os
from datetime import datetime
from itertools import islice

import click

import database_connection  # noqa: F401
from matrix_connection import matrix_client
from mongoengine.errors import FieldDoesNotExist, ValidationError
from schema import Message

MATRIX_ROOM_IDS = os.environ['MATRIX_ROOM_IDS'].split(',')

MESSAGE_EVENT_TYPES = {'m.room.message', 'm.room.message.feedback'}


def get_room_events(room_id):
    """Iterate room events, starting at the cursor."""
    room = matrix_client().get_rooms()[room_id]
    print(f"Reading events from room {room.display_name!r}…")
    yield from room.events
    batch_size = 1000  # empirically, this is the largest honored value
    prev_batch = room.prev_batch
    while True:
        res = room.client.api.get_room_messages(room.room_id, prev_batch, 'b',
                                                limit=batch_size)
        events = res['chunk']
        if not events:
            break
        print(f"Read {len(events)} events...")
        yield from events
        prev_batch = res['end']


def import_events(room_id, limit=None):
    events = get_room_events(room_id)
    # restrict to messages
    messages = (event for event in events if event['type'] in MESSAGE_EVENT_TYPES)
    # exclude redacted messages
    messages = (event for event in messages if 'redacted_because' not in event)
    # exclude messages that have already been saved
    messages = (event for event in messages
                if not Message.objects(event_id=event['event_id'],
                                       room_id=event['room_id']))
    if limit:
        messages = islice(messages, limit)
    for event in messages:
        fields = event.copy()
        fields['messageType'] = fields.pop('type')
        fields['room_id'] = room_id
        fields['timestamp'] = datetime.fromtimestamp(
            fields.pop('origin_server_ts') / 1000)
        fields.pop('age', None)
        fields.pop('unsigned', None)
        try:
            message = Message(**replace_dots(fields))
        except (FieldDoesNotExist, ValidationError):
            print(fields)
            raise

        message.save()
        yield message


def replace_dots(obj):
    """Recursively replace '.' by '•' in dictionary key names, to avoid mongodb
    error.
    """
    return {k.replace('.', '•'): replace_dots(v) for k, v in obj.items()} \
        if isinstance(obj, dict) \
        else obj



@click.command()
@click.option('--limit', type=int)
def cli(limit):
    """Import events."""
    for room_id in MATRIX_ROOM_IDS:
        import_count = sum(1 for _ in import_events(room_id, limit))
        print(f"Imported {import_count} messages")
    print(f"The database now has {Message.objects.count()} messages")


if __name__ == '__main__':
    cli()
