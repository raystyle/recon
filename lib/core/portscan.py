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
        self.make_ports()
        # self.ports = ports if ports else "80,443,8080,8081,7001,8888,8880,3128,9080,9090,9200,9300"
        self.ret = []
        self.loop = loop

    def make_ports(self):
        # 80
        # 80-90
        # 8000-9090
        # 7001,7002 weblogic
        # 9200,9300 elasticsearch
        # 6379 redis未授权
        # 5984 CouchDB http://xxx:5984/_utils/
        # 11211 memcache未授权访问
        # 27017,27018 Mongodb未授权访问
        ports = [80,7001,7002,9200,9300,6379,5984,11211,27017,27018]
        ports.extend([i for i in range(81,91)])
        ports.extend([i for i in range(8000,9091)])
        self.ports = ports

    @staticmethod
    async def socket(host, port, loop):
        conn = asyncio.open_connection(host, int(port), loop=loop)
        try:
            reader, writer = await asyncio.wait_for(conn, timeout=2)
            return True
        except:
            return False

    async def run(self):
        logger.info("Check host: " + self.host + " ports")
        # self.ports = self.ports.split(",")
        for port in self.ports:
            flag = await PortScanner.socket(self.host, port, self.loop)
            if flag:
                self.ret.append(self.host+":"+str(port))
                logger.info("Found "+self.host+":"+str(port))

def port_scan(subdomains, ports=None):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    scanners = [PortScanner(subdomain,ports,loop) for subdomain in subdomains]
    tasks = []
    for scanner in scanners:
        tasks.append(asyncio.ensure_future(scanner.run()))
    for task in tasks:
        loop.run_until_complete(task)
    loop.close()
    ret = []
    for scanner in scanners:
        if len(scanner.ret) > 0:
            ret.extend(scanner.ret)
    return ret