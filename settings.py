workers = 2

server_addr = ('127.0.0.1', 8000)

logger = 'geweb'
logformat = u'%(asctime)s %(process)d %(filename)s:%(lineno)d:%(funcName)s %(levelname)s  %(message)s'
logfile = None
loglevel = 'debug'

apps = []

template_path = 'templates'

try:
    from settings_local import *
except ImportError:
    pass
