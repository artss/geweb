# HTTP server workers quantity
workers = 2

# Server host and port tuple
server_addr = ('127.0.0.1', 8000)

# Logger settings
logger = 'geweb'
logformat = u'%(asctime)s %(process)d %(filename)s:%(lineno)d:%(funcName)s %(levelname)s  %(message)s'
logfile = None
loglevel = 'debug'

# Domain
domain = 'example.com'

# Enabled applications list.
apps = []

# Path to templates
template_path = 'templates'

# Debug
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

# Override settings by settings_local
try:
    from settings_local import *
except ImportError:
    pass
