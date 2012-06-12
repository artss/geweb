workers = 2

server_addr = ('127.0.0.1', 8000)

logger = 'geweb'
logformat = u'%(asctime)s %(process)d %(filename)s:%(lineno)d:%(funcName)s %(levelname)s  %(message)s'
logfile = None
loglevel = 'debug'

domain = None

apps = []

template_path = 'templates'

debug = False

# File sessions
#session_backend = 'geweb.session.file.FileBackend'
#session_dir = '/tmp'

# Redis sessions
#session_backend = 'geweb.session.redis.RedisBackend'
#session_socket = 'tcp://127.0.0.1:6379'
#session_db = 0

session_cookie = 'sessid'
session_expires = 30 # days

try:
    from settings_local import *
except ImportError:
    pass
