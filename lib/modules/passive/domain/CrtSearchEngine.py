#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain.engine import Engine,aiohttp,ERROR
import re

class CrtSearchEngine(Engine):
    """
    need a proxy
    """
    def __init__(self,target,random=True,proxy=False):
        self.engine = "https://crt.sh"
        self.base_url = 'https://crt.sh/?q=%25.{domain}'
        super(CrtSearchEngine, self)\
            .__init__(target, engine_name="SSL Certificates",random=random,proxy=proxy)

    def extract(self, content):
        pattern = re.compile('<TD>(.*?{domain})</TD>'.format(domain=self.target.netloc))
        try:
            links = pattern.findall(content)
            for link in links:
                link = link.strip('*.')
                if link != self.target.netloc and link not in self.subdomains:
                    self.logger.info(
                        "{engine} Found {subdomain}".format(
                            engine=self.engine_name, subdomain=link))
                    self.subdomains.update([link])
        except Exception:
            pass

    def format_base_url(self,*args):
        return self.base_url.format(domain=args[0])

    def check_response_errors(self,content):
        if not content:
            return [False, ERROR.TIMEOUT]

        if "None found" in content:
            return [False,ERROR.END]
        elif "crt.sh ID" in content:
            return [True,0]
        else:
            return [False,ERROR.UNKNOWN]


    async def run(self):

        async with aiohttp.ClientSession() as session:
            if not self.check_engine_available(session, self.engine):
                self.logger.error("{engine_name} is not available, skipping!"
                                  .format(engine_name=self.engine_name))
                return
            self.logger.info("{engine_name} is available, starting!"
                             .format(engine_name=self.engine_name))

            url = self.format_base_url(self.target.netloc)

            self.logger.debug("{engine} {url}".format(engine=self.engine_name,url=url))

            content = await Engine.get(session, url, self.headers,timeout=50)

            ret = self.check_response_errors(content)
            if not ret[0]:
                self.deal_with_errors(ret[1])
                return
            self.extract(content)

    def deal_with_errors(self,error_code):
        """subclass should override this function for identify security mechanism"""
        if error_code == ERROR.END:
            self.logger.warning("{engine} has no results".format(engine=self.engine_name))
        elif error_code == ERROR.UNKNOWN:
            # raise ReconResponseContentErrorException
            self.logger.error("response content error")
        elif error_code == ERROR.TIMEOUT:
            self.logger.warning("{engine} is not available now, Stop!".format(engine=self.engine_name))

