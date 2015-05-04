from geweb import log
from geweb.exceptions import NotFound
from fnmatch import fnmatch

try:
    import re2 as re
except ImportError:
    import re

import settings

routes = []

# route decorator
def route(pattern, methods=None, host=None):
    def wrapper(view):
        routes.append(R(pattern, view, methods=methods, host=host))
    return wrapper

def resolve(request):
    if not routes:
        return welcome()

    for r in routes:
        try:
            return r.resolve(request)
        except R.NotMatched:
            continue

    raise NotFound

def welcome():
    from geweb.template import render
    return render('geweb/welcome.html')

# route instance
class R(object):
    def __init__(self, pattern, view, methods=None, host=None):
        self.pattern = re.compile(r'^%s$' % pattern)

        if methods:
            if not isinstance(methods, (list, tuple)):
                methods = [methods]
            self.methods = map(lambda m: m.upper(), methods)
        else:
            self.methods = None

        self.host = host

        self.view = view

    def resolve(self, request):
        if self.methods and request.method.upper() not in self.methods:
            raise R.NotMatched

        if self.host and not fnmatch(request.host, self.host):
            raise R.NotMatched

        m = re.match(self.pattern, request.path)
        if not m:
            raise R.NotMatched

        log.debug('%s resolved to %s' % (request, self.view))
        return self.view(**m.groupdict())

    class NotMatched(Exception):
        pass

for app in settings.apps:
    urls = __import__("%s.urls" % app, globals(), locals(), 'urls', -1)
    try:
        routes.extend([r for r in urls.urls])
    except AttributeError:
        pass

__all__ = ['R', 'route', 'resolve']

