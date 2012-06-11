import os
import urlparse
from cgi import FieldStorage
from datetime import datetime
from hashlib import md5

from geweb import log

import settings

class Request(object):

    def __init__(self, http_request):
        self.method = http_request.typestr

        self.uri = http_request.uri

        path = urlparse.urlparse(self.uri)
        self.path = path.path

        self.host = http_request.find_input_header('Host')

        self.remote_host = http_request.find_input_header('X-Forwarded-For') \
                           or http_request.remote_host
        self.remote_port = http_request.remote_port

        self.referer = http_request.find_input_header('Referer')
        self.is_xhr = http_request.find_input_header('X-Requested-With') \
                      == 'XMLHttpRequest'
        self._args = {}
        self._files = {}

        if self.method in ('POST', 'PUT'):
            ctype = http_request.find_input_header('Content-Type')
            clen = http_request.find_input_header('Content-Length')

            if ctype == 'application/x-www-form-urlencoded':
                self._args = urlparse.parse_qs(http_request.input_buffer.read())

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
        elif self.method == 'GET':
            self._args = urlparse.parse_qs(path.query)

        self._headers = {}
        for hname, hvalue in http_request.get_input_headers():
            self._headers[hname.lower()] = hvalue

    def args(self, arg, default=None):
        try:
            return self._args[arg]
        except KeyError:
            return default

    def files(self, filename):
        try:
            return self._files[filename]
        except KeyError:
            return None

    def header(self, hname):
        try:
            return self._headers[hname.lower()]
        except KeyError:
            return None

