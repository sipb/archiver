#
# Database interface
#

from . import config

import random
import sqlalchemy
import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()
_session_class = sqlalchemy.orm.sessionmaker()

# Engine cache, indexed by URL
_engines = {}

def _get_database(name):
    url = 'mysql://%(user)s:%(password)s@%(host)s/%(name)s' % config.get().databases[name]
    if url not in _engines:
        _engines[url] = sqlalchemy.create_engine(url)
    return _session_class(bind=_engines[url])

def _noop():
    pass

def _master_fail():
    raise ValueError("Called a writing method with a slave database")

def master():
    """Returns a new session with the master database."""

    session = _get_database(config.get().database['master'])
    session.is_master = True
    session.check_master = _noop
    return session

def slave():
    """Returns a new session with a slave database."""

    db = random.choice(config.get().database['slaves'])
    session = _get_database(db)
    session.is_master = False
    session.check_master = _master_fail
    return session

