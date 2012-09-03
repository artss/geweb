import os, sys
import gevent
from gevent import monkey; monkey.patch_all()
from gevent import http as ghttp

import settings

try:
    sys.path.extend(settings.libs)
except AttributeError:
    pass

import traceback
from time import time

from geweb import log
from geweb.http import Request, Response
from geweb.route import route
from geweb.exceptions import HTTPError, InternalServerError
from geweb.template import render, TemplateNotFound
from geweb.env import env

def _handler(http_request):
    """
    HTTP request handler.
    """

    if settings.debug:
        tm = time()

    env.request = Request(http_request)

    try:
        code = 200
        message = 'OK'
        response = route(env.request.path)

    except HTTPError, e:
        code = e.code
        message = e.message

        try:
            response = render(['/%d.html'%code,'/50x.html', 'geweb/50x.html'],
                              code=code, message=message)
        except TemplateNotFound, e:
            response = 'No error template found'

    except Exception, e:
        code = InternalServerError.code
        message = InternalServerError.message
        if settings.debug:
            response = render('geweb/debug.html', code=code, message=message,
                              trace=traceback.format_exc())
        else:
            response = render('/50x.html', code=code, message=message)

    if isinstance(response, (str, unicode)):
        response = Response(response)
    elif response is None:
        response = Response('')

    cookies = response.cookie_out()
    for c in cookies:
        http_request.add_output_header('Set-Cookie', c)

    redirect = response.redirect()
    if redirect:
        http_request.add_output_header('Location', redirect)
        http_request.send_reply(302, 'Moved Temporarily',
                                str('redirect %s' % redirect))
    else:
        http_request.add_output_header("Content-Type", response.mimetype)
        http_request.send_reply(code, message, response.body.encode('utf-8'))

    if settings.debug:
        tm = round(time() - tm, 4)
    else:
        tm = ''

    log.info('%s %s %s %d %s' % (tm, env.request.remote_host,
                              env.request.method, code, env.request.uri))

def run_server(host=None, port=None, workers=None, debug=None,
               logfile=None, stdout=None, loglevel=None):
    """
    Start the HTTP server.
    Optional arguments, which override settings:
    host - host (IP address) to listen
    port - port number to listen
    worker - number of worker processes
    debug - debug mode
    logfile - path to log file
    stdout - write log to stdout instead of log file
    loglevel - log level
    """

    if stdout:
        settings.logfile = None
    elif logfile:
        settings.logfile = logfile

    if loglevel:
        settings.loglevel = loglevel

    log.init()

    if host is not None:
        settings.server_host = host
    if port is not None:
        settings.server_port = port

    if workers is not None:
        settings.workers = workers

    if debug:
        settings.debug = True

    log.info('Starting HTTP server at %s:%d' % \
             (settings.server_host, settings.server_port))

    httpd = ghttp.HTTPServer((settings.server_host, settings.server_port),
                             lambda req: gevent.spawn(_handler, req))
    httpd.pre_start()

    for i in xrange(settings.workers - 1):
        pid = gevent.fork()
        if pid == 0:
            break

    try:
        log.info('Starting worker PID=%d' % os.getpid())
        httpd.serve_forever()
    except Exception, e:
        log.error('%s: %s' % (e.__class__.__name__, str(e)))
        httpd.stop()
        log.error('Worker PID=%d is stopped' % os.getpid())

