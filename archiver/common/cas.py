#
# Interfaces to the content-addressable storage.
#

import base64
import hashlib
import sqlalchemy as sql

from . import database

def _hash(data):
    """Constructs hash of the data object used to identify that object."""

    hasher = hashlib.sha384()
    hasher.update(data)
    return base64.b64encode(hasher.digest(), "_-")

class DataObject(database.Base):
    __tablename__ = 'data_objects'

    hash = sql.Column(sql.BINARY(64), primary_key=True)
    order_key = sql.Column(sql.Integer(), autoincrement=True)
    properties = sql.Column(sql.BINARY(1024))
    value = sql.Column(sql.LargeBinary)

    def __init__(self, hash, value):
        self.hash = hash
        self.properties = '{}'
        self.value = value

    def data():
        """Returns the contents of the object."""

        return self.value

def get(db, hash):
    """Requests the object by its ID for reading."""

    return db.query(DataObject).get(hash)

def add(db, value):
    """Adds the value to the storage if it's not there yet. Returns the hash
    of the added value."""

    db.check_master()

    hash = _hash(value)
    if not db.query(DataObject).get(hash):
        obj = DataObject(hash, value)
        db.add(obj)
    return hash

