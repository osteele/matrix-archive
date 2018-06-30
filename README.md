# Matrix Message Importer

Import messages from a matrix.org room, for research, archival, and
preservation.

Developed at [Dinacon 2018](https://www.dinacon.org), for use by the
documentation team.

Use this responsibly and ethically. Don't use people's messages that
without their knowledge and consent.

## Setup

Install Pipenv. Run `pipenv install`.

Set these environment variables: `MATRIX_USER`, `MATRIX_PASSWORD`,
`MATRIX_ROOM_IDS`.

`MATRIX_ROOM_IDS` should be a comma-separated list of Matrix room IDs (or a
single id). Run `pipenv run list_rooms.py` to list the room ids.

Set `MONGODB_URI` to a MongoDB connection URL, *or* install a local MongoDB
instance.

## Usage

`pipenv run import_messages.py` imports the messages into the database.

`pipenv run export_messages.py filename.html` exports a text, HTML, JSON, or
YAML file. The file contains links to the image download URLs on the Matrix
server.

## References

[Matrix Client-Server API](https://matrix.org/docs/spec/r0.0.0/client_server.html)

## License

MIT
