from geweb import log
from geweb.exceptions import NotFound, Forbidden

try:
    import re2 as re
except ImportError:
    import re

import settings

urls_list = []

for app in settings.apps:
    urls = __import__("%s.urls" % app, globals(), locals(), 'urls', -1)
    for item in urls.urls:
        try:
            regex, methods, view = item
            if not isinstance(methods, (list, tuple)):
                methods = [methods]
            methods = map(lambda m: m.lower(), methods)
        except ValueError:
            regex, view = item
            methods = None
        urls_list.append((re.compile(regex), methods, view))

def route(method, path):
    if not urls_list:
        return welcome()

    for regex, methods, view in urls_list:
        if methods and method.lower() not in methods:
            raise Forbidden
        m = re.match(regex, path)
        if m:
            return view(**m.groupdict())

    raise NotFound

def welcome():
    from geweb.template import render
    return render('geweb/welcome.html')

