#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    author:  wh1t3P1g  <wh1t3P1g@gmail.com>
    description:
        framework global data
'''

from lib.core.dataType import AttribDict
from lib.core.log import LOGGER

# config dict
conf = AttribDict()
# results
kb = AttribDict()
# logger
logger = LOGGER

# logger.setLevel(10) # debug
# loger.setLevel(40) # error
# logger.setLevel(20) # info
