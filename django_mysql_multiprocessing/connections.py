import os
from typing import Dict

from django.conf import settings
from django.core import signals
from django.db import connections
from django.db.backends.mysql.base import DatabaseWrapper
from django.db.utils import ConnectionHandler

__all__ = ['apply_patch']


_original_get_item = ConnectionHandler.__getitem__


class ConnectionPid:
    def __init__(self, alias):
        self._alias = alias

    def acquire(self):
        # create new instance of connection
        db_settings = settings.DATABASES[self._alias]
        db_settings.setdefault('ATOMIC_REQUESTS', False)
        db_settings.setdefault('AUTOCOMMIT', True)
        db_settings.setdefault('ENGINE', 'django.db.backends.dummy')
        if db_settings['ENGINE'] == 'django.db.backends.' or not db_settings['ENGINE']:
            db_settings['ENGINE'] = 'django.db.backends.dummy'
        db_settings.setdefault('CONN_MAX_AGE', 0)
        db_settings.setdefault('OPTIONS', {})
        db_settings.setdefault('TIME_ZONE', None)
        conn = DatabaseWrapper(db_settings)
        return conn

    def release(self, conn):
        conn.close()


def _new_get_item(self, alias):
    pid = os.getpid()

    # reuse green-let local for conn inside a single request
    if hasattr(self._connections, '{}-{}'.format(alias, pid)):
        return getattr(self._connections, '{}-{}'.format(alias, pid))

    # reuse conn from connection pool and bind to green-let local
    if not hasattr(ConnectionHandler, 'connection_pid'):
        ConnectionHandler.connection_pid = {}

    if alias not in self.connection_pid:
        self.connection_pid[alias] = ConnectionPid(alias)

    conn = self.connection_pid[alias].acquire()
    conn.close_if_unusable_or_obsolete()
    setattr(self._connections, '{}-{}'.format(alias, pid), conn)
    return conn


def recycle_old_connections(**_):
    ConnectionHandler.connection_pid: Dict[str, ConnectionPid]
    aliases = []
    for alias in connections:
        aliases.append(alias)
        conn = connections[alias]
        ConnectionHandler.connection_pid[alias].release(conn)

    for alias in aliases:
        del connections[alias]


def apply_patch():
    signals.request_finished.connect(recycle_old_connections)
    ConnectionHandler.__getitem__ = _new_get_item
