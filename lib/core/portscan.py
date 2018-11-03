#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.core.data import logger
import backoff as backoff
import async_timeout
import asyncio,uvloop,aiohttp

class PortScanner(object):

    def __init__(self, host, ports=None):
        self.host = host
        self.ports = ports if ports else "80,443,8080,8081"
        self.ret = []

    @staticmethod
    @backoff.on_exception(backoff.expo, TimeoutError, max_tries=2)
    async def get(session, url, method='GET', data=None, proxy=False, timeout=20):
        """
        fetch online resource
        :param session: aiohttp session
        :param url: like http://baidu.com/s?
        :param headers: use normal http headers to fetch online resource
        :param proxy: proxy url
        :return: online resource content
        """
        try:
            async with async_timeout.timeout(timeout):
                if not proxy:
                    async with session.request(method, url, data=data) as response:
                        return await response.text()
                else:
                    async with session.request(method, url, data=data, proxy=proxy) as response:
                        return await response.text()
        except Exception as e:
            # logger.warning('fetch exception: {e} {u}'.format(e=type(e).__name__, u=url))
            return None

    async def run(self):
        logger.info("Check host: "+self.host+" ports: "+self.ports)
        self.ports = self.ports.split(",")
        async with aiohttp.ClientSession() as session:
            for port in self.ports:
                if port == "443":
                    url = "https://"+self.host
                else:
                    url = "http://"+self.host+":"+port
                try:
                    flag = await PortScanner.get(session, url, timeout=2)
                    if flag:
                        self.ret.append(self.host+":"+port)
                except Exception as e:
                    logger.warning('fetch exception: {e} {u}'.format(e=type(e).__name__, u=url))


def port_scan(subdomains, ports=None):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    scanners = [PortScanner(subdomain,ports) for subdomain in subdomains]
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