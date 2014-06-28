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
        self.protocol = http_request.find_input_header('X-Forwarded-Proto') \
                        or 'http'
        self.method = http_request.typestr

        self.uri = http_request.uri

        path = urlparse.urlparse(self.uri)
        self.path = path.path

        self._headers = {}
        self.headers_dict = {}
        for name, value in http_request.get_input_headers():
            self._headers[name.lower()] = value
            self.headers_dict[name] = value

        self.host = self.header('Host')

        self.remote_host = self.header('X-Forwarded-For') or \
                           http_request.remote_host
        self.remote_port = http_request.remote_port

        self.user_agent = self.header('User-Agent')

        self.referer = self.header('Referer')
        self.is_xhr = self.header('X-Requested-With') == 'XMLHttpRequest'

        self._args = {}
        self._files = {}

        if self.method in ('GET', 'HEAD'):
            self._args = urlparse.parse_qs(path.query)

        elif self.method in ('POST', 'PUT', 'DELETE'):
            ctype = http_request.find_input_header('Content-Type')
            clen = http_request.find_input_header('Content-Length')

            if not ctype or ctype.startswith('application/x-www-form-urlencoded'):
                _buf = http_request.input_buffer.read(-1)
                self._args = urlparse.parse_qs(_buf)

            elif ctype.startswith('multipart/form-data'):
                form = FieldStorage(fp=http_request.input_buffer,
                                    environ={
                                        'REQUEST_METHOD': self.method,
                                        'CONTENT_TYPE': ctype,
                                        'CONTENT_LENGTH': clen
                                    }, keep_blank_values=True)

                for field in form.list:
                    try:
                        if not field.filename:
                            raise AttributeError

                        pos = field.filename.rfind('/')
                        if pos == -1:
                            pos = field.filename.rfind('\\')
                        filename = field.filename[pos+1:]
                        try:
                            if not isinstance(self._args[field.name], (list, tuple)):
                                self._args[field.name] = [self._args[field.name]]
                            self._args[field.name].append(filename)
                        except KeyError:
                            self._args[field.name] = filename

                        tmpfile = '%s.%s' % \
                                  (filename,
                                   md5(datetime.now().isoformat()).hexdigest())
                        try:
                            upload_dir = settings.upload_dir
                        except AttributeError:
                            upload_dir = '/tmp' # FIXME: get from environment

                        tmpfile_path = os.path.join(upload_dir, tmpfile)
                        try:
                            if not isinstance(self._files[field.name], (list, tuple)):
                                self._files[field.name] = [self._files[field.name]]
                            self._files[field.name].append(tmpfile_path)
                        except KeyError:
                            self._files[field.name] = tmpfile_path
                        fd = open(tmpfile_path, 'w')
                        while True:
                            b = field.file.read(4096)
                            if b == '':
                                break
                            fd.write(b)
                        fd.close()
                        log.info('Upload %s: %s' % (field.name, field.filename))
                    except AttributeError:
                        self._args[field.name] = form.getvalue(field.name)
                    except IOError, e:
                        log.error('Cannot write %s: %s' % \
                                  (self._files[field.name], e.strerror))

                del form

        self._cookies = Cookie(self.header('Cookie'))
        for c, v in self._cookies.iteritems():
            log.debug('Cookie: %s=%s' % (c, v.value))

    def args(self, arg=None, default=None):
        if arg is None:
            return self._args
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

