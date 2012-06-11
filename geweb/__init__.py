import os
import gevent
from gevent import http as ghttp

import settings

from geweb import log
from geweb.http import Request, Response
from geweb.route import route
from geweb.exceptions import HTTPError

def handler(http_request):
    request = Request(http_request)

    try:
        response = route(request)
        message = 'OK'
        code = 200
    except HTTPError, e:
        response = e.message
        message = e.message
        code = e.code

    log.info('%s %d %s' % (request.method, code, request.uri))

    if isinstance(response, (str, unicode)):
        response = Response(response)

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

