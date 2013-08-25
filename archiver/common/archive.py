#
# Representation of a single archive
#

import sqlalchemy as sql
import sqlalchemy.orm as orm

from . import database

class Archive(database.Base):
    __tablename__ = 'archives'

    id = sql.Column(sql.Integer(), primary_key=True, autoincrement=True)
    name = sql.Column(sql.BINARY(255), unique=True)
    description = sql.Column(sql.LargeBinary())
    active = sql.Column(sql.Boolean())
    deleted = sql.Column(sql.Boolean())

    # FIXME: I have no ACL classes to relate to yet
    owner_acl = sql.Column(sql.Integer())
    mod_acl = sql.Column(sql.Integer())
    read_acl = sql.Column(sql.Integer())

def get_by_name(db, name):
    return db.query(Archive).filter_by(name=name).first()

