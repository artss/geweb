import sys
import contextlib

import gevent
from gevent.queue import Queue
from gevent.socket import wait_read, wait_write
from psycopg2 import extensions, OperationalError, connect
extensions.register_type(extensions.UNICODE)
extensions.register_type(extensions.UNICODEARRAY)
from psycopg2.extras import DictConnection
import time
from geweb.util import Singleton
from geweb import log

def gevent_wait_callback(conn, timeout=None):
    """A wait callback useful to allow gevent to work with Psycopg."""
    while 1:
        state = conn.poll()
        if state == extensions.POLL_OK:
            break
        elif state == extensions.POLL_READ:
            wait_read(conn.fileno(), timeout=timeout)
        elif state == extensions.POLL_WRITE:
            wait_write(conn.fileno(), timeout=timeout)
        else:
            raise OperationalError(
                "Bad result from poll: %r" % state)


extensions.set_wait_callback(gevent_wait_callback)


class DatabaseConnectionPool(object):

    def __init__(self, maxsize=100, debug=False):
        if not isinstance(maxsize, (int, long)):
            raise TypeError('Expected integer, got %r' % (maxsize, ))
        self.maxsize = maxsize
        self.pool = Queue()
        self.size = 0
        self.debug = debug

    def get(self):
        pool = self.pool
        if self.size >= self.maxsize or pool.qsize():
            return pool.get()
        else:
            self.size += 1
            try:
                new_item = self.create_connection()
            except:
                self.size -= 1
                raise
            return new_item

    def put(self, item):
        self.pool.put(item)

    def closeall(self):
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
            except Exception:
                pass

    @contextlib.contextmanager
    def connection(self):
        conn = self.get()
        try:
            yield conn
        except:
            if conn.closed:
                conn = None
                self.closeall()
            else:
                conn = self._rollback(conn)
            raise
        else:
            if conn.closed:
                raise OperationalError("Cannot commit because connection was closed: %r" % (conn, ))
            conn.commit()
        finally:
            if conn is not None and not conn.closed:
                self.put(conn)

    @contextlib.contextmanager
    def cursor(self, *args, **kwargs):
        conn = self.get()
        try:
            yield conn.cursor(*args, **kwargs)
        except:
            if conn.closed:
                conn = None
                self.closeall()
            else:
                conn = self._rollback(conn)
            raise
        else:
            if conn.closed:
                raise OperationalError("Cannot commit because connection was closed: %r" % (conn, ))
            conn.commit()
        finally:
            if conn is not None and not conn.closed:
                self.put(conn)

    def _rollback(self, conn):
        try:
            conn.rollback()
        except:
            gevent.get_hub().handle_error(conn, *sys.exc_info())
            return
        return conn

    def execute(self, *args, **kwargs):
        with self.cursor() as cursor:
            t = ''
            if self.debug:
                t1 = time.time()
            cursor.execute(*args, **kwargs)
            if self.debug:
                t = '%.3f' % (time.time() - t1)
            try:
                log.debug('fetchone %s %s' % \
                          (t, cursor.mogrify(*args, **kwargs)))
            except:
                pass

    def fetchone(self, *args, **kwargs):
        with self.cursor() as cursor:
            t = ''
            if self.debug:
                t1 = time.time()
            cursor.execute(*args, **kwargs)
            if self.debug:
                t = '%.3f' % (time.time() - t1)
            try:
                log.debug('fetchone %s %s' % \
                          (t, cursor.mogrify(*args, **kwargs)))
            except:
                pass
            return cursor.fetchone()

    def fetchall(self, *args, **kwargs):
        with self.cursor() as cursor:
            t = ''
            if self.debug:
                t1 = time.time()
            cursor.execute(*args, **kwargs)
            if self.debug:
                t = ' %.3f' % (time.time() - t1)
            try:
                log.debug('fetchone %s %s' % (t, cursor.mogrify(*args, **kwargs)))
            except:
                pass
            return cursor.fetchall()


class PostgresConnectionPool(Singleton, DatabaseConnectionPool):
    def __init__(self, debug=False, *args, **kwargs):
        self.connect = kwargs.pop('connect', connect)
        maxsize = kwargs.pop('maxsize', None)
        self.args = args
        self.kwargs = kwargs
        DatabaseConnectionPool.__init__(self, debug, maxsize)

    def create_connection(self):
        conn = self.connect(*self.args, connection_factory=DictConnection,
                            **self.kwargs)
        conn.set_client_encoding('UTF8')
        return conn

