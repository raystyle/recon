#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''

class ReconBaseException(Exception):
    pass

class ReconInvalidURLException(ReconBaseException):
    """
    url is not a valid domain
    """
    pass

class ReconResponseContentErrorException(ReconBaseException):
    """
    response content is not a valid content
    """
    pass
