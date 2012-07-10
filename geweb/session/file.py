import os
try:
    import simplejson as json
except ImportError:
    import json
from datetime import datetime

from geweb.session import SessionBackend
from geweb import log

import settings

class FileBackend(SessionBackend):
    """
    Local files session storage.
    """
    def __init__(self, sessid):
        self._loaded = False
        try:
            path = settings.session_dir
        except AttributeError:
            path = '/tmp'

        self.filename = os.path.join(path, 'geweb-session.%s' % sessid)
        log.debug('FileBackend: %s' % self.filename)

    def get(self):
        try:
            fd = open(self.filename)
            data = json.loads(fd.read())
        except (ValueError, IOError):
            data = {}
        finally:
            try:
                fd.close()
            except:
                pass
        return data

    def save(self, data):
        dthandler = lambda obj: obj.isoformat() \
                                if isinstance(obj, datetime) else None
        fd = open(self.filename, 'w')
        fd.write(json.dumps(data, default=dthandler))
        fd.close()

    def destroy(self):
        try:
            os.unlink(self.filename)
        except OSError, e:
            log.error('unlink %s: %s' % (self.filename, e.strerror))
