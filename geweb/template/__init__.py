import os
from jinja2 import Environment, PrefixLoader, FileSystemLoader
from jinja2 import TemplateNotFound

from geweb.template.filters import filters

from geweb.env import env

from geweb.util import csrf_token

from datetime import datetime

import settings

geweb_template_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   '..', 'data', 'templates'))
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
                        autoescape=True, cache_size=-1,
                        extensions=['jinja2.ext.loopcontrols'])

for name, fn in filters.iteritems():
    jinja_env.filters[name] = fn

def render(names, **context):
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
            return tmpl.render(context, settings=settings, env=env,
                               __now__=datetime.now(),
                               csrf_token=csrf_token)
        except TemplateNotFound:
            continue

    raise TemplateNotFound('')

