#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
import asyncio
import aiodns
import socket

loop = asyncio.get_event_loop()
resolver = aiodns.DNSResolver(loop=loop)
f = resolver.gethostbyname("www.baidu.com",socket.AF_INET)
try:
    result = loop.run_until_complete(f)
    print(result)
except:
    pass
