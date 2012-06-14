import os
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
        try:
            path = settings.session_dir
        except AttributeError:
            path = '/tmp'

        self.filename = os.path.join(path, 'geweb-session.%s' % sessid)
        log.debug('FileBackend: %s' % self.filename)

    def get(self):
        fd = open(self.filename)
        try:
            data = json.loads(fd.read())
        except ValueError:
            data = {}
        fd.close()
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
