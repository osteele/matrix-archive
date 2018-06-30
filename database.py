import os
import re

from mongoengine import connect

MONGODB_URI = os.getenv('MONGODB_URI')
MONGO_RE = (r'mongodb://'
            r'(?P<username>.+?)'
            r':(?P<password>.+?)'
            r'@(?P<host>(?:.+?):(?:\d+))'
            r'/(?P<db>.+)')

if MONGODB_URI:
    print(f"Connecting to {MONGODB_URI}")
    connect_args = re.match(MONGO_RE, MONGODB_URI).groupdict()
    connect(**connect_args)
else:
    connect('matrix')
