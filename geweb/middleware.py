from geweb import log

_middleware = {}

class MiddlewareError(Exception):
    pass

class Middleware(object):
    def process_request(self, request):
        pass

    def process_response(self, response):
        pass

def register_middleware(middleware):
    try:
        if _middleware[middleware]:
            return
    except KeyError:
        pass

    log.debug('Importing %s middleware', middleware)

    if isinstance(middleware, (str, unicode)):
        module, cls = middleware.rsplit('.', 1)
        try:
            module = __import__(module, globals(), locals(), cls, -1)
            cls = getattr(module, cls)
        except (ImportError, AttributeError), e:
            print e
            raise MiddlewareError('%s: %s' % (middleware, e))
    else:
        cls = middleware
        middleware = middleware.__name__

    _middleware[middleware] = cls()

def unregister_middleware(middleware):
    if not isinstance(middleware, (str, unicode)):
        middleware = middleware.__name__
    try:
        del _middleware[middleware]
    except KeyError:
        pass

def process_request(request):
    for m in _middleware:
        _middleware[m].process_request(request)

def process_response(response):
    for m in _middleware:
        _middleware[m].process_response(response)

