#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain.engine import Engine,ERROR,urlparse
import re

class ChinazEngine(Engine):

    def __init__(self,target,random=True,proxy=False):
        self.engine = "http://tool.chinaz.com"
        self.base_url = 'http://tool.chinaz.com/subdomain?domain={query}&page={page_no}'
        super(ChinazEngine,self).__init__(target,engine_name="Chinaz",random=random,proxy=proxy)

    def generate_query(self):
        length = len(self.subdomains)
        query = self.target.netloc
        if length==0:
            self.queries.append((query,1))
        else:
            self.queries.append((query,self.pre_pageno+1))

    def check_response_errors(self,content):
        if not content:
            return [False, ERROR.TIMEOUT]

        if "没有查询到" in content:
            return [False,ERROR.END]
        elif "被访问网址" in content:
            return [True,0]
        else:
            return [False,ERROR.UNKNOWN]

    def extract(self,content):
        pattern = re.compile('<a href="javascript:" onclick="window.open.*?" target="_blank">(.*?{domain})</a>'
                             .format(domain=self.target.netloc))
        next_page = "下一页"
        try:
            links = pattern.findall(content)

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
        except Exception:
            pass
        if next_page in content:
            # tell engine there still be next page
            return True
        else:
            return False