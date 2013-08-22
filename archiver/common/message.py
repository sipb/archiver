#
# Routines related to processing the messages themselves.
#

import datetime
import email.parser
import email.utils
import json
import sqlalchemy as sql
import sqlalchemy.orm as orm

from . import cas
from . import database
from .archive import Archive

class ArchivedMessage(database.Base):
    __tablename__ = 'messages'

    id = sql.Column(sql.BIGINT(), primary_key=True, autoincrement=True)
    archive_id = sql.Column('archive', sql.Integer(), sql.ForeignKey('archives.id'))
    timestamp = sql.Column(sql.DateTime())
    deleted = sql.Column(sql.Boolean())
    message_id = sql.Column(sql.VARBINARY(512))
    sender = sql.Column(sql.VARBINARY(255))
    tree = sql.Column(sql.Binary(2**24))

    archive = orm.relationship("Archive", backref=orm.backref('messages', order_by=id))

class Header(database.Base):
    __tablename__ = 'headers'

    id = sql.Column(sql.BIGINT(), primary_key=True, autoincrement=True)
    message_id = sql.Column('message', sql.BIGINT(), sql.ForeignKey('messages.id'))
    name = sql.Column(sql.VARBINARY(1024))
    value = sql.Column(sql.LargeBinary())

    message = orm.relationship("ArchivedMessage", backref=orm.backref('headers', order_by=name))

    def __init__(self, message, name, value):
        self.message = message
        self.name = name
        self.value = value

class Party(database.Base):
    __tablename__ = 'parties'

    id = sql.Column(sql.BIGINT(), primary_key=True, autoincrement=True)
    message_id = sql.Column('message', sql.BIGINT(), sql.ForeignKey('messages.id'))
    type = sql.Column(sql.Enum('From', 'To', 'Cc', 'Bcc'))
    address = sql.Column(sql.VARBINARY(255))
    value = sql.Column(sql.VARBINARY(512))

    message = orm.relationship("ArchivedMessage", backref=orm.backref('parties', order_by=type))

    def __init__(self, message, type, address, value):
        self.message = message
        self.type = type
        self.address = address
        self.value = value

def from_message_object(db, msg, sender):
    """Creates an ArchivedMessage object from Message object from email.message
    module."""

    db.check_master()

    obj = ArchivedMessage()
    obj.timestamp = datetime.datetime.utcnow()
    obj.deleted = False
    obj.message_id = msg["Message-ID"]
    obj.sender = sender

    obj.headers = [Header(obj, name, value) for name, value in msg.items()]
    for header in obj.headers:
        if header.name in {'From', 'To', 'Cc', 'Bcc'}:
            real_name, address = email.utils.parseaddr(header.value)
            party = Party(obj, header.name, address, real_name)
            obj.parties.append(party)

    def convert_nested_message(message, top_level = False):
        if top_level:
            # Leave only content-related headers for tree purposes, do not
            # dupluicate all the headers. Also, leave From and Subject for
            # display purposes
            node = {k : v for k, v in message.items() if
                k.startswith("Content-") or k == 'From' or k == 'Subject'}
        else:
            node = dict(message)
        if message.is_multipart():
            node['contents'] = map(convert_nested_message, message.get_payload())
        else:
            node['contents'] = cas.add(db, message.get_payload(decode=True))

        return node

    obj.tree = convert_nested_message(msg, True)

    return obj

def from_stream(db, fp, sender):
    parser = email.parser.Parser()
    msg = parser.parse(fp)
    return from_message_object(db, msg, sender)

