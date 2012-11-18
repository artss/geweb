import os
import urlparse
from cgi import FieldStorage
from Cookie import Cookie
from datetime import datetime, timedelta
import time
from hashlib import md5

from geweb import log
from geweb.env import env

import settings

class Request(object):

    def __init__(self, http_request):
        self.method = http_request.typestr

        self.uri = http_request.uri

        path = urlparse.urlparse(self.uri)
        self.path = path.path

        self._headers = {}
        for name, value in http_request.get_input_headers():
            self._headers[name.lower()] = value

        self.host = self.header('Host')

        self.remote_host = self.header('X-Forwarded-For') or \
                           http_request.remote_host
        self.remote_port = http_request.remote_port

        self.user_agent = self.header('User-Agent')

        self.referer = self.header('Referer')
        self.is_xhr = self.header('X-Requested-With') == 'XMLHttpRequest'

        self._args = {}
        self._files = {}

        if self.method == 'GET':
            self._args = urlparse.parse_qs(path.query)

        elif self.method in ('POST', 'PUT'):
            ctype = http_request.find_input_header('Content-Type')
            clen = http_request.find_input_header('Content-Length')

            if not ctype or ctype.startswith('application/x-www-form-urlencoded'):
                self._args = urlparse.parse_qs(
                                    http_request.input_buffer.read())

            elif ctype.startswith('multipart/form-data'):
                form = FieldStorage(fp=http_request.input_buffer,
                                    environ={
                                        'REQUEST_METHOD': self.method,
                                        'CONTENT_TYPE': ctype,
                                        'CONTENT_LENGTH': clen
                                    }, keep_blank_values=True)

                for f in form.keys():
                    try:
                        if not form[f].filename:
                            raise AttributeError

                        pos = form[f].filename.rfind('/')
                        if pos == -1:
                            pos = form[f].filename.rfind('\\')
                        self._args[f] = form[f].filename[pos+1:]

                        tmpfile = '%s.%s' % \
                                  (self._args[f],
                                   md5(datetime.now().isoformat()).hexdigest())
                        try:
                            upload_dir = settings.upload_dir
                        except AttributeError:
                            upload_dir = '/tmp' # FIXME: get from environment
                        self._files[f] = os.path.join(upload_dir, tmpfile)
                        fd = open(self._files[f], 'w')
                        while True:
                            b = form[f].file.read(4096)
                            if b == '':
                                break
                            fd.write(b)
                        fd.close()
                        log.info('Upload %s: %s' % (f, form[f].filename))
                    except AttributeError:
                        self._args[f] = form.getvalue(f)
                    except IOError, e:
                        log.error('Cannot write %s: %s' % \
                                  (self._files[f], e.strerror))

                del form

        self._cookies = Cookie(self.header('Cookie'))
        for c, v in self._cookies.iteritems():
            log.debug('Cookie: %s=%s' % (c, v.value))

    def args(self, arg, default=None):
        try:
            if len(self._args[arg]) == 1:
                return self._args[arg][0]
            return self._args[arg]
        except KeyError:
            return default

    def files(self, filename):
        try:
            return self._files[filename]
        except KeyError:
            return None

    def header(self, name):
        try:
            return self._headers[name.lower()]
        except KeyError:
            return None

    def cookie(self, name, default=None):
        try:
            return self._cookies[name].value
        except KeyError:
            return default

class Response(object):

    def __init__(self, body='', code=200, message='OK', mimetype='text/html',
                       redirect=None, headers={}):
        self.code = code
        self.message = message
        self.mimetype = mimetype
        self.body = body
        self._headers = headers
        self._cookies = Cookie()

        self._redirect = redirect

    def header(self, name, value):
        self._headers[name] = value

    def set_cookie(self, name, value, domain=None, path=None, expires=None,
                         secure=False, httponly=False):
        self._cookies[name] = value
        if domain:
            self._cookies[name]['domain'] = domain

        if path:
            self._cookies[name]['path'] = path
        if expires:
            self._cookies[name]['expires'] = time.asctime(expires.timetuple())
        if secure:
            self._cookies[name]['secure'] = secure
        if httponly:
            self._cookies[name]['httponly'] = httponly

    def delete_cookie(self, name, domain=None, path=None):
        self.set_cookie(name, '', domain=domain, path=path,
                                  expires=datetime.now()-timedelta(days=30))

    def cookie_out(self):
        out = []
        for c in self._cookies:
            out.append(self._cookies[c].output(header='').strip())
        if out:
            log.debug('Set-Cookies: %s' % (out))
        return out

    def redirect(self, url=None):
        if url is None:
            return self._redirect
        self._redirect = url

