#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain.engine import Engine,urlparse,ERROR
from random import randint
import re
import asyncio

class YahooEngine(Engine):
    """
    need a proxy
    """

    def __init__(self,target,random=True,proxy=False):
        self.MAX_PAGENO = 20
        self.engine = "https://search.yahoo.com"
        self.base_url = 'https://search.yahoo.com/search?p={query}&b={page_no}'
        self.find_new_domain = False
        super(YahooEngine, self)\
            .__init__(target, engine_name="Yahoo",random=random, proxy=proxy)

    def extract(self, content):
        next_page = re.compile('<a class="next".*?>Next</a>')
        pattern = re.compile('<span class=.{1,100}?>(.{0,100}?<b.{0,100}?>'+self.target.netloc+'</b>)')
        try:
            links = pattern.findall(content)
            self.find_new_domain = False
            for link in links:
                link = re.sub('<.*?>','',link)

                if not link.startswith('http://') and not link.startswith('https://'):
                    link = "http://" + link
                subdomain = urlparse.urlparse(link).netloc

                if subdomain != self.target.netloc and subdomain.endswith(self.target.netloc):
                    if subdomain not in self.subdomains:
                        self.logger.info(
                        "{engine} Found {subdomain}".format(
                                engine=self.engine_name,subdomain=subdomain))
                        self.subdomains.update([subdomain])
                        self.find_new_domain = True
        except Exception:
            pass
        if next_page.findall(content):
            # tell engine there still be next page
            return True
        else:
            return False

    def generate_query(self):
        if self.check_max_pageno(): return
        length = len(self.subdomains)

        if length==0:
            query = "site:{domain}".format(domain=self.target.netloc)
            self.queries.append((query,0))
            self.subdomains.update(["www."+self.target.netloc])# 防止 一直请求第一个页面
        elif self.find_new_domain:
            found = ' -site:'.join(list(self.subdomains))
            query = "site:{domain} -site:{found}".format(domain=self.target.netloc, found=found)
            self.queries.append((query, 0))
        else:
            self.queries.append((self.pre_query,self.pre_pageno+1))

    def format_base_url(self, *args):
        return self.base_url.format(query=args[0], page_no=args[1]*10+1)

    def check_response_errors(self,content):
        if not content:
            return [False, ERROR.TIMEOUT]

        if "We did not find results for" in content:
            return [False,ERROR.END]
        elif " results</span>" in content:
            return [True,0]
        else:
            return [False,ERROR.UNKNOWN]

    async def should_sleep(self):
        self.logger.warning("{engine} sleep random time...".format(engine=self.engine_name))
        await asyncio.sleep(randint(1, 3))
