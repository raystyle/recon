#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.core.data import logger
import asyncio,uvloop
import aiodns,socket

class PortScanner(object):

    def __init__(self, host, ports=None, loop=None):
        self.host = host
        self.ports = ports
        self.ret = []
        self.loop = loop

    # def make_ports(self):
    #     # 80
    #     # 80-90
    #     # 8000-9090
    #     # 7001,7002 weblogic
    #     # 9200,9300 elasticsearch
    #     # 6379 redis未授权
    #     # 5984 CouchDB http://xxx:5984/_utils/
    #     # 11211 memcache未授权访问
    #     # 27017,27018 Mongodb未授权访问
    #     ports = [80,7001,7002,9200,9300,6379,5984,11211,27017,27018]
    #     ports.extend([i for i in range(81,91)])
    #     ports.extend([i for i in range(8000,9091)])
    #     self.ports = ports

    @staticmethod
    async def socket(host, port, loop):
        conn = asyncio.open_connection(host, int(port), loop=loop)
        try:
            reader, writer = await asyncio.wait_for(conn, timeout=0.5)
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
        logger.info("Check host: " + self.host + " ports done")

def check_host(subdomains,loop):
    resolver = aiodns.DNSResolver(loop=loop)
    ret = []
    for subdomain in subdomains:
        task = resolver.gethostbyname(subdomain,socket.AF_INET)
        try:
            result = loop.run_until_complete(task)
            ret.append(subdomain)
        except:
            pass
    # for task in tasks:
    #     try:
    #         result = loop.run_until_complete(task)
    #         ret.append(result.name)
    #     except:
    #         pass
    return ret
def make_ports(type):
    base = [80, 443, 8080, 8081,8888, 8880, 7001, 7002, 9200, 9300, 6379, 5984, 11211, 27017, 27018]
    if type == "small":
        return base
    elif type == "large":
        base.extend([i for i in range(81, 91)])
        base.extend([i for i in range(8000, 9091)])
        base = list(set(base))
    return base
def port_scan(subdomains, ports=None):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    subdomains = check_host(subdomains,loop)
    ports = make_ports(ports)
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


if __name__ == "__main__":
    subdomains = ["xueji.ucas.ac.cn","m.baidu.com"]
    port_scan(subdomains,"large")