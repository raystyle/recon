#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.core.data import logger
import asyncio,uvloop

class PortScanner(object):

    def __init__(self, host, ports=None, loop=None):
        self.host = host
        self.ports = ports if ports else "80,443,8080,8081,7001,8888,8880"
        self.ret = []
        self.loop = loop

    @staticmethod
    async def socket(host, port, loop):
        conn = asyncio.open_connection(host, int(port), loop=loop)
        try:
            await asyncio.wait_for(conn, timeout=2)
            return True
        except:
            return False

    async def run(self):
        logger.info("Check host: " + self.host + " ports: " + self.ports)
        self.ports = self.ports.split(",")
        for port in self.ports:
            flag = await PortScanner.socket(self.host, port, self.loop)
            if flag:
                self.ret.append(self.host+":"+port)
                logger.info("Found "+self.host+":"+port)

def assign(scanners,loop):
    tasks = []  # todo 控制一下速度 太快会崩
    for scanner in scanners:
        tasks.append(asyncio.ensure_future(scanner.run()))
    for task in tasks:
        loop.run_until_complete(task)

def port_scan(subdomains, ports=None):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    scanners = [PortScanner(subdomain,ports,loop) for subdomain in subdomains]
    step = 30
    start = step
    tmp = scanners[0:step]
    while tmp:
        assign(tmp,loop)
        tmp = scanners[start:start+step]
        start += step
    loop.close()
    ret = []
    for scanner in scanners:
        if len(scanner.ret) > 0:
            ret.extend(scanner.ret)
    return ret