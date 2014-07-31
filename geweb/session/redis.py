try:
    import simplejson as json
except ImportError:
    import json
from datetime import datetime

from geweb.session import SessionBackend
from geweb.util.redispool import RedisPool
from geweb import log

import settings

class RedisBackend(SessionBackend):
    """
    Redis session storage.
    """
    def __init__(self, sessid):
        try:
            addr = settings.session_socket
        except AttributeError:
            addr = 'tcp://127.0.0.1:6379'
        try:
            db = int(settings.session_db)
        except AttributeError:
            db = 0

        self.redis = RedisPool(addr, db)
        try:
            prefix = settings.session_prefix
        except AttributeError:
            prefix = 'geweb-session-'
        self.key = '%s%s' % (prefix, sessid)

    def get(self):
        try:
            data = json.loads(self.redis.get(self.key))
        except (TypeError, ValueError):
            data = {}
        return data

    def save(self, data):
        dthandler = lambda obj: obj.isoformat() \
                                if isinstance(obj, datetime) else None
        self.redis.set(self.key, json.dumps(data, default=dthandler))
        try:
            self.redis.expire(self.key, settings.session_expires*86400)
        except AttributeError:
            pass

        log.debug('RedisBackend.save: %s' % self.key)

    def destroy(self):
        self.redis.delete(self.key)
