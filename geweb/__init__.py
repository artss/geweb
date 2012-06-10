import os
import gevent
from gevent import http

import settings

from geweb import log
from geweb.route import route

def handler(r):
    print '-- handler'
    return route(r)

def run_server():
    log.info('Starting HTTP server at %s:%d' % settings.server_addr)

    httpd = http.HTTPServer(settings.server_addr,
                            lambda r: gevent.spawn(handler, r))
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

