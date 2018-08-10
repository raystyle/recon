#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain.engine import Engine,ERROR,aiohttp
import re
class VirustotalEngine(Engine):
    """need a proxy"""
    def __init__(self,target,random=True,proxy=False):
        self.engine = "https://www.virustotal.com"
        self.base_url = 'https://www.virustotal.com/en/domain/{domain}/information/'
        super(VirustotalEngine, self)\
            .__init__(target, engine_name="Virustotal",random=random, proxy=proxy)

    def format_base_url(self, *args):
        return self.base_url.format(domain=args[0])

    def check_response_errors(self,content):
        if not content:
            return [False, ERROR.TIMEOUT]
        if 'No IP addresses' in content:
            return [False,ERROR.END]
        elif 'Observed subdomains' in content:
            return [True,0]
        else:
            return [False,ERROR.UNKNOWN]

    def extract(self,content):
        pattern = re.compile('<div class="enum .*?">\s*<a target="_blank" href=".*?">\s*(.*?{domain})\s*</a>'
                             .format(domain=self.target.netloc))
        try:
            links = pattern.findall(content)
            for link in links:
                if link != self.target.netloc and link not in self.subdomains:
                    self.logger.info(
                        "{engine} Found {subdomain}".format(
                            engine=self.engine_name, subdomain=link))
                    self.subdomains.update([link])
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

            url = self.format_base_url(self.target.netloc)

            self.logger.debug("{engine} {url}".format(engine=self.engine_name,url=url))

            content = await Engine.get(session, url, headers=self.headers, proxy=self.proxy)

            ret = self.check_response_errors(content)
            if not ret[0]:
                self.deal_with_errors(ret[1])
                return

            self.extract(content)

            self.logger.debug(self.engine_name + " " + str(len(self.subdomains)))