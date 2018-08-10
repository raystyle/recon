#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
import backoff as backoff
from lib.core.data import logger
from lib.core.common import random_ua
from urllib import parse as urlparse
from lib.core.enums import default_headers,ERROR
import async_timeout
from lib.core.common import check_domain
from lib.core.exceptions import ReconResponseContentErrorException
import aiohttp
from collections import deque

class Engine(object):

    def __init__(self, target,engine_name=None,random=True, headers=None, proxy=False,timeout=20):
        self.headers = None if not random else random_ua()
        self.proxy = proxy
        self.target = check_domain(target)
        self.logger = logger
        self.engine_name = engine_name
        self.subdomains = set() # not include original domain(self.target)
        self.headers = headers if headers else default_headers
        self.queries = deque()
        self.pre_query = ""
        self.pre_pageno = 0
        self.timeout = timeout

    @staticmethod
    @backoff.on_exception(backoff.expo, TimeoutError, max_tries=3)
    async def get(session,url,headers,method='GET',data=None,proxy=False,timeout=20):
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
                    async with session.request(method,url,data=data,headers=headers) as response:
                        return await response.text()
                else:
                    async with session.request(method,url,data=data,headers=headers,proxy=proxy) as response:
                        return await response.text()
        except Exception as e:
            logger.warning('fetch exception: {e} {u}'.format(e=type(e).__name__, u=url))
            return None

    def check_engine_available(self,session,engine):
        if self.get(session,engine,headers=None):
            return True
        else:
            return False

    def print_(self):
        self.logger.info("Searching now in {engine_name}..".format(engine_name=self.engine_name))
        return

    def extract(self,content):
        """subclass override this function for extracting domain from response"""
        return

    async def should_sleep(self):
        """subclass should override this function for pause http request, avoiding be blocked"""
        return

    def generate_query(self):
        """subclass should override this function for generate queries
            append to queries
            according subdomains generate queries
            or according page content generate next page
            demo:
                if check_max_pageno(): return
                generate query and append to self.queries
                suggest generate 10 query one time
        """
        return

    def format_base_url(self, *args):
        """
        subclass should override this function for specific format
        :param args:
        :return:
        """
        return self.base_url.format(query=args[0], page_no=args[1])

    def check_max_pageno(self):
        return self.MAX_PAGENO <= self.pre_pageno

    def check_response_errors(self,content):
        """subclass should override this function for identify security mechanism"""
        return True

    def deal_with_errors(self,error_code):
        """subclass should override this function for identify security mechanism"""
        if error_code == ERROR.END:
            self.logger.warning("{engine} has no results".format(engine=self.engine_name))
        elif error_code == ERROR.UNKNOWN:
            self.logger.error("{engine} response content error".format(engine=self.engine_name))
            # raise ReconResponseContentErrorException
        elif error_code == ERROR.TIMEOUT:
            self.logger.warning("{engine} is not available now, Stop!".format(engine=self.engine_name))

    async def run(self):
        async with aiohttp.ClientSession() as session:

            if not self.check_engine_available(session,self.engine):
                self.logger.error("{engine_name} is not available, skipping!"
                                  .format(engine_name=self.engine_name))
                return
            self.logger.info("{engine_name} is available, starting!"
                             .format(engine_name=self.engine_name))

            self.generate_query()
            while len(self.queries):
                session.cookie_jar.clear()
                (query, self.pre_pageno) = self.queries.popleft()
                self.pre_query = query
                url = self.format_base_url(query,self.pre_pageno)

                self.logger.debug("{engine} {url}".format(engine=self.engine_name,url=url))

                content = await Engine.get(session,
                                           url,
                                           headers=self.headers,
                                           timeout=self.timeout,
                                           proxy=self.proxy)

                ret = self.check_response_errors(content)
                if not ret[0]:
                    self.deal_with_errors(ret[1])
                    break

                if self.extract(content):
                    self.generate_query()
                if len(self.queries)>0:
                    await self.should_sleep()# avoid being blocked
                self.logger.debug(self.engine_name + " " + str(len(self.subdomains)))

if __name__ == '__main__':
    engine = Engine("")