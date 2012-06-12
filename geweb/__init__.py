import os
import gevent
from gevent import http as ghttp

import settings

if settings.debug:
    import traceback

from geweb import log
from geweb.http import Request, Response
from geweb.route import route
from geweb.exceptions import HTTPError, InternalServerError
from geweb.template import render, TemplateNotFound

def handler(http_request):
    request = Request(http_request)

    try:
        code = 200
        message = 'OK'
        response = route(request)

    except HTTPError, e:
        code = e.code
        message = e.message

        try:
            response = render('/%d.html' % code, code=code, message=message)
        except TemplateNotFound, e:
            response = render('/50x.html', code=code, message=message)

    except Exception, e:
        code = InternalServerError.code
        message = InternalServerError.message
        if settings.debug:
            response = render('/50x.debug.html', code=code, message=message,
                              trace=traceback.format_exc(),
                              locals=locals(), globals=globals())
        else:
            response = render('/50x.html', code=code, message=message)

    log.info('%s %d %s' % (request.method, code, request.uri))

    if isinstance(response, (str, unicode)):
        response = Response(response)

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

def run_server():
    log.info('Starting HTTP server at %s:%d' % settings.server_addr)

    httpd = ghttp.HTTPServer(settings.server_addr,
                             lambda req: gevent.spawn(handler, req))
    httpd.pre_start()

    for i in xrange(settings.workers - 1):
        pid = gevent.fork()
        if pid == 0:
            break

    try:
        log.info('Starting worker PID=%d' % os.getpid())
        httpd.serve_forever()
    except Exception, e:
        log.error("%s: %s" % (e.__class__.__name__, str(e)))
        httpd.stop()

