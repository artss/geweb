#!/usr/bin/env python

import os
import sys
from geweb import log
from geweb import run_server

try:
    import settings
except ImportError:
    print "Cannot find settings.py in %r." % os.getcwd()

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        log.info('Server is stopped')
        sys.exit()

