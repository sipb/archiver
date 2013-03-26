#
# Database interface
#

from . import config

import sqlalchemy

_singleton_master = None
_singleton_slave  = None

def _get_database(name):
    url = 'mysql://%(user)s:%(password)s@%(host)s/%(name)s' % config.get().databases[name]
    return sqlalchemy.create_engine(url)

def master():
    global _singleton_master
    if not _singleton_master:
        _singleton_master = _get_database(config.get().database['master'])
    return _singleton_master

def slave():
    global _singleton_slave
    if not _singleton_slave:
        config = random.choice(config.get().database['slave'])
        _singleton_slave = _get_database(config)
    return _singleton_slave

