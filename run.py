#!/usr/bin/env python

import sys
from geweb import log
from geweb import run_server

try:
    run_server()
except KeyboardInterrupt:
    log.info('Server is stopped')
    sys.exit()

