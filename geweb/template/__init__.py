import os
from jinja2 import Environment, PrefixLoader, FileSystemLoader

from geweb.template.filters import filters

import settings

_loaders = {'': FileSystemLoader(settings.template_path)}

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

def render(name, **context):
    tmpl = jinja_env.get_template(name)
    return tmpl.render(context)

