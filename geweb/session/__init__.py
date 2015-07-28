from hashlib import sha1
from random import randint
from time import time
from datetime import datetime, timedelta

from geweb.env import env
from geweb.middleware import Middleware

import settings

class Session(object):
    """
    Sessions implementation.
    Requires any backend inherited from geweb.session.SessionBackend.

    Usage:

    Create or update session:
    sess = Session()
    sess['key'] = value
    sess.save()

    Destroy session:
    sess = Session()
    sess.destroy()
    """
    def __init__(self, sessid=None):
        """
        Start a new session or use an existing one.
        """
        if sessid:
            self.sessid = sessid
        else:
            try:
                self.sessid = env._sessid
            except KeyError:
                self.sessid = env.request.header('authorization')
                if not self.sessid:
                    self.sessid = env.request.cookie(settings.session_cookie)
                env._sessid = self.sessid

        self._data = {}

        if self.sessid:
            self.backend = backend_cls(self.sessid)
            self._data = self.backend.get()


        #register_middleware(SessionMiddleware)

    def __setitem__(self, item, value):
        self._data[item] = value

    def __getitem__(self, item):
        if not self._data:
            if self.sessid:
                self._data = self.backend.get()
            else:
                return None
        try:
            return self._data[item]
        except KeyError:
            return None

    def __delitem__(self, item):
        if not self._data and self.sessid:
            self._data = self.backend.get()
        try:
            del self._data[item]
        except KeyError:
            pass

    def new(self):
        """
        Force start a new session.
        Session data will not be removed.
        """
        t = time()
        rnd = randint(1000000000, 10000000000)
        self.sessid = sha1('%s%s' % (t, rnd)).hexdigest()
        self.backend = backend_cls(self.sessid)

    def save(self):
        """
        Save session data.
        """

        if not self._data:
            return

        if not self.sessid:
            self.new()
        self.backend.save(self._data)
        env._sessid = self.sessid

    def destroy(self):
        """
        Destroy the session.
        """
        if not self.sessid:
            return
        self.backend.destroy()
        env._session_destroy = True

class SessionBackend(object):
    def __init__(self, sessid):
        """
        Session backend abstraction.
        """
        pass

    def get(self):
        """
        Get data from storage.
        """
        return {}

    def save(self, data):
        """
        Save data to storage.
        """
        pass

    def destroy(self):
        """
        Remove session data.
        """
        pass

try:
    backend_name = settings.session_backend
except AttributeError:
    backend_name = 'geweb.session.file.FileBackend'

module, cls = backend_name.rsplit('.', 1)
backend_cls = getattr(__import__(module, globals(), locals(), [cls], -1), cls)

class SessionMiddleware(Middleware):
    def process_response(self, response):
        try:
            sessid = env._sessid
        except KeyError:
            try:
                if env._session_destroy:
                    response.delete_cookie(settings.session_cookie,
                                           domain='.%s' % settings.domain,
                                           path='/')
            except KeyError:
                pass
            return
        expire = datetime.now() + timedelta(days=settings.session_expire)
        response.set_cookie(settings.session_cookie, sessid,
                            domain='.%s' % settings.domain, path='/',
                            #secure=True,
                            httponly=True,
                            expires=expire)

