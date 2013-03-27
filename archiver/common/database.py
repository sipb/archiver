#
# Database interface
#

from . import config

import random
import sqlalchemy
import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()

_singleton_master = None
_singleton_slave  = None

def _get_database(name):
    url = 'mysql://%(user)s:%(password)s@%(host)s/%(name)s' % config.get().databases[name]
    engine = sqlalchemy.create_engine(url, echo=True)
    session_class = sqlalchemy.orm.sessionmaker()
    return session_class(bind=engine)

def master():
    global _singleton_master
    if not _singleton_master:
        _singleton_master = _get_database(config.get().database['master'])
    return _singleton_master

def slave():
    global _singleton_slave
    if not _singleton_slave:
        db = random.choice(config.get().database['slaves'])
        _singleton_slave = _get_database(db)
    return _singleton_slave

