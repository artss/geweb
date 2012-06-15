import logging

import settings

levels = {
    'error': logging.ERROR,
    'warn': logging.WARN,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
level = levels[settings.loglevel.lower()]

try:
    format = settings.logformat
except AttributeError:
    format = '%(asctime)s %(levelname)s: %(message)s'

_log = logging.getLogger(settings.logger)

info = _log.info
error = _log.error
warn = _log.warn
debug = _log.debug

def init():
    logging.basicConfig(format=format, filename=settings.logfile, level=level)
    _log = logging.getLogger(settings.logger)

    global info
    global error
    global warn
    global debug
    info = _log.info
    error = _log.error
    warn = _log.warn
    debug = _log.debug

