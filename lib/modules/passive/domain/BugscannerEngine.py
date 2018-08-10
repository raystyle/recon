#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain.engine import Engine,aiohttp,ERROR
import json

class BugscannerEngine(Engine):

    def __init__(self,target,random=True,proxy=False):
        self.engine = "http://tools.bugscaner.com"
        self.base_url = 'http://tools.bugscaner.com/api/subdomain/'
        self.find_new_domain = False
        super(BugscannerEngine, self).__init__(target, engine_name="Bugscanner",random=random,proxy=proxy)

    def check_response_errors(self,content):
        if not content:
            return [False, ERROR.TIMEOUT]

        if "{\"code\": 404}" in content:
            return [False,ERROR.END]
        elif "\"nb\":" in content:
            return [True,0]
        else:
            return [False,ERROR.UNKNOWN]

    def extract(self,content):
        try:
            domain = json.loads(content)['domain']
            self.subdomains.update(domain)
        except Exception:
            pass

    async def run(self):
        async with aiohttp.ClientSession() as session:

            if not self.check_engine_available(session,self.engine):
                self.logger.error("{engine_name} is not available, skipping!"
                                  .format(engine_name=self.engine_name))
                return
            self.logger.info("{engine_name} is available, starting!"
                             .format(engine_name=self.engine_name))

            data = {
                'inputurl':self.target.netloc
            }
            content = await Engine.get(session,
                                       self.base_url,
                                       method="POST",
                                       data=data,
                                       headers=self.headers,
                                       timeout=self.timeout,
                                       proxy=self.proxy)

            ret = self.check_response_errors(content)
            if not ret[0]:
                self.deal_with_errors(ret[1])

            self.extract(content)
            self.logger.info("{engine} Found {num} sites".format(engine=self.engine_name,num=len(self.subdomains)))
            self.logger.debug(self.engine_name + " " + str(len(self.subdomains)))
