#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain.engine import Engine,ERROR,urlparse
import re,asyncio
from random import randint

class NetcraftEngine(Engine):

    def __init__(self,target,random=True,proxy=False):
        self.engine = "https://searchdns.netcraft.com"
        self.base_url = 'https://searchdns.netcraft.com/' \
                        '?restriction=site+ends+with&host={domain}' \
                        '&last={last_domain}&from={page_no}'
        self.last_domain = ''
        self.find_new_domain = False
        super(NetcraftEngine, self)\
            .__init__(target, engine_name="Netcraft",random=random, proxy=proxy,timeout=50)

    def extract(self, content):
        next_page = re.compile('<A.*?>\s*<b>Next page</b>\s*</a>')
        pattern = re.compile('<a href="http[s]*://(.*{domain}).*?" rel="nofollow">'
                             .format(domain=self.target.netloc))
        try:
            links = pattern.findall(content)
            self.last_domain=self.target.netloc
            for link in links:
                if not link.startswith('http://') and not link.startswith('https://'):
                    link = "http://" + link
                subdomain = urlparse.urlparse(link).netloc

                if subdomain != self.target.netloc and subdomain.endswith(self.target.netloc):
                    if subdomain not in self.subdomains:
                        self.logger.info(
                        "{engine} Found {subdomain}".format(
                                engine=self.engine_name,subdomain=subdomain))
                        self.subdomains.update([subdomain])
                self.last_domain = subdomain
        except Exception:
            pass
        if next_page.findall(content):
            # tell engine there still be next page
            return True
        else:
            return False

    def check_response_errors(self,content):
        if not content:
            return [False, ERROR.TIMEOUT]
        pattern = re.compile('Found (\d*) site')
        ret = pattern.findall(content)
        if ret:
            if int(ret[0]) == 0:
                return [False, ERROR.END]
            else:
                return [True, 0]
        else:
            return [False,ERROR.UNKNOWN]

    def generate_query(self):
        length = len(self.subdomains)
        query = self.target.netloc
        if length==0:
            self.queries.append((query,0))
        else:
            self.queries.append((query,self.pre_pageno+1))

    def format_base_url(self, *args):
        if self.last_domain == self.target.netloc or not self.last_domain:
            self.last_domain = ''
        return self.base_url.format(domain=args[0],last_domain=self.last_domain,page_no=args[1]*20+1)

    async def should_sleep(self):
        self.logger.warning("{engine} sleep random time...".format(engine=self.engine_name))
        await asyncio.sleep(randint(1, 2))