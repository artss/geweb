import os
from jinja2 import Environment, PrefixLoader, FileSystemLoader
from jinja2 import TemplateNotFound

from geweb.http import Response
from geweb.template.filters import filters

from geweb.env import env

import settings

geweb_template_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   '..', 'data', 'templates'))
print '>>>', geweb_template_path

_loaders = {
    '': FileSystemLoader(settings.template_path),
    'geweb': FileSystemLoader(geweb_template_path),
}

for appname in settings.apps:
    app = __import__(appname, globals(), locals(), [appname, 'filters'], -1)

    path = os.path.join(app.__path__[0], 'templates')
    if os.path.exists(path):
        _loaders[appname] = FileSystemLoader(path)

    try:
        filters.update(app.filters.filters)
    except AttributeError:
        pass

jinja_env = Environment(loader=PrefixLoader(_loaders),
                        autoescape=True, cache_size=-1)

for name, fn in filters.iteritems():
    jinja_env.filters[name] = fn

def render_string(names, **context):
    """
    Render a string from template.

    Usage:
    string = render_string('template.html', var1='value 1', var2='value 2')
    """
    if isinstance(names, (str, unicode)):
        names = [names]

    for name in names:
        try:
            tmpl = jinja_env.get_template(name)
            return tmpl.render(context, settings=settings, env=env)
        except TemplateNotFound:
            continue

    raise TemplateNotFound('')

def render(names, mimetype='text/html', **context):
    """
    Render HTTP response from template.

    Usage:
    response = render('template.html', var1='value 1', var2='value 2')
    """
    return Response(render_string(names, **context), mimetype=mimetype)

