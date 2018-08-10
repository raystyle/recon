#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    author:  wh1t3P1g  <wh1t3P1g@gmail.com>
    description:
        framework logger
'''

import logging
import sys

LOGGER = logging.getLogger()

LOGGER_HANDLER = None
try:
    from thirdparty.ansistrm.ansistrm import ColorizingStreamHandler

    LOGGER_HANDLER = ColorizingStreamHandler(sys.stdout)
except ImportError:
    LOGGER_HANDLER = logging.StreamHandler(sys.stdout)

FORMATTER = logging.Formatter("\r[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

LOGGER_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(LOGGER_HANDLER)

LOGGER.setLevel(logging.INFO)

if __name__=='__main__':
    LOGGER.debug('DEBUG')
    LOGGER.info('INFO')
    LOGGER.warning('WARNING')
    LOGGER.error('ERROR')
    LOGGER.critical('CRITICAL')

