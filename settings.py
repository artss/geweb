workers = 2

server_addr = ('127.0.0.1', 8000)

logger = 'geweb'
logfile = None
loglevel = 'debug'

try:
    from settings_local import *
except ImportError:
    pass
