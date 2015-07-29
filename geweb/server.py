import sys
import settings
try:
    sys.path.extend(settings.libs)
except AttributeError:
    pass

import gevent
from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
from gevent.wsgi import WSGIServer
from setproctitle import setproctitle
import inspect
import traceback
from time import time

from geweb import log
from geweb.http import Request, Response
from geweb.route import resolve
from geweb.exceptions import GewebError, InternalServerError
from geweb.template import render, TemplateNotFound
from geweb.mail import mail
from geweb.middleware import register_middleware, \
                             process_request, process_response
from geweb.env import env

try:
    if not isinstance(settings.middleware, (list, tuple)):
        settings.middleware = [settings.middleware]
    for m in settings.middleware:
        register_middleware(m)
except AttributeError:
    pass

def handle(environ, start_response):
    tm = time()

    env.request = Request(environ)
    process_request(env.request)

    code = None
    message = None
    try:
        response = resolve(env.request)

    except GewebError, e:
        code = e.code
        message = e.message

        try:
            response = Response(template=['/errors/%s.html' % e.__class__.__name__,
                               '/%d.html' % code, '/50x.html',
                               'geweb/50x.html'],
                               error=e)
        except TemplateNotFound, e:
            response = 'No error template found'

    except Exception, e:
        code = InternalServerError.code
        message = InternalServerError.message

        trace = traceback.format_exc()
        tb = inspect.trace()[-1][0]

        if isinstance(trace, str):
            trace = trace.decode('utf-8')
        log.error("%s: %s" % (code, trace))

        subject = 'Error at %s: %s' % (settings.domain, e.__class__.__name__)
        body = render('geweb/report.html',
                code=code, message=message,
                protocol=env.request.protocol, host=env.request.host,
                uri=env.request.uri, method=env.request.method,
                params=env.request.args().iteritems(),
                headers=env.request.headers(),
                globals=tb.f_globals.iteritems(),
                locals=tb.f_locals.iteritems(),
                exception=e, trace=trace)

        if settings.debug:
            response = Response(body, code=code, message=message)
        else:
            response = render('/50x.html', code=code, message=message)
            mail(settings.report_mail, subject=subject, body=body, html=True)

    if isinstance(response, (str, unicode)):
        response = Response(response)
    elif response is None:
        response = Response('')
    if not code or not message:
        code = response.code
        message = response.message
    process_response(response)

    status, headers = response.render_headers()
    body = response.render()

    if isinstance(body, unicode):
        body = body.encode('utf-8')

    if settings.debug:
        tm = round(time() - tm, 4)
    else:
        tm = ''

    log.info('[%s] %d %s' % (tm, code, env.request))

    start_response(status, headers)
    return [body]

def run_server(host=None, port=None, workers=None, debug=None,
               logfile=None, stdout=None, loglevel=None):
    if not host:
        host = settings.server_host
    if not port:
        port = settings.server_port

    if workers is not None:
        settings.workers = workers

    if debug:
        settings.debug = True

    try:
        proctitle = settings.proctitle
    except AttributeError:
        proctitle = 'geweb'
    setproctitle(proctitle)

    log.info('Starting HTTP server at %s:%d' % (host, port))

    pool = Pool(10000)
    server = WSGIServer("%s:%s" % (host, port), handle, spawn=pool)
    server.init_socket()

    for i in xrange(settings.workers - 1):
        pid = gevent.fork()
        if pid == 0:
            break

    server.serve_forever()

