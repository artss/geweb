from hashlib import sha1
from random import randint
from time import time
from datetime import datetime, timedelta

from geweb.env import env
from geweb.http import wrap_response

import settings

class Session(object):
    def __init__(self):
        self.sessid = env.request.cookie(settings.session_cookie)
        self._data = {}
        if self.sessid:
            self.backend = backend_cls(self.sessid)

    def __setitem__(self, attr, value):
        self._data[attr] = value

    def __getitem__(self, attr):
        if not self._data:
            if self.sessid:
                self._data = self.backend.get()
            else:
                return None
        try:
            return self._data[attr]
        except KeyError:
            return None

    def new(self):
        t = time()
        rnd = randint(1000000000, 10000000000)
        self.sessid = sha1('%s%s' % (t, rnd)).hexdigest()
        self.backend = backend_cls(self.sessid)

    def save(self):
        if not self.sessid:
            self.new()
        self.backend.save(self._data)
        def set_cookie(response):
            expires = datetime.now() + timedelta(days=settings.session_expires)
            response.set_cookie(settings.session_cookie, self.sessid,
                                domain='.%s' % settings.domain, path='/',
                                expires=expires)
        wrap_response(set_cookie)


    def destroy(self):
        if not self.sessid:
            return
        self.backend.destroy()
        def delete_cookie(response):
            response.delete_cookie(settings.session_cookie,
                                   domain='.%s' % settings.domain, path='/')
        wrap_response(delete_cookie)

class SessionBackend(object):
    def __init__(self, sessid):
        pass

    def get(self):
        return {}

    def save(self, data):
        pass

    def destroy(self):
        pass

try:
    backend_name = settings.session_backend
except AttributeError:
    backend_name = 'geweb.session.file.FileBackend'

module, cls = backend_name.rsplit('.', 1)
backend_cls = getattr(__import__(module, globals(), locals(), [cls], -1), cls)

