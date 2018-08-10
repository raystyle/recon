#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain.engine import Engine,ERROR,urlparse
import re

class AskEngine(Engine):
    """
    this engine need a proxy
    """
    def __init__(self,target,random=True,proxy=False):
        self.MAX_PAGENO = 30
        self.engine = "http://www.ask.com"
        self.base_url = 'http://www.ask.com/web?q={query}&page={page_no}' \
                        '&o=0&l=dir&qsrc=998&qo=pagination'
        self.find_new_domain = False
        super(AskEngine, self).__init__(target, engine_name="Ask",random=random,proxy=proxy)

    def extract(self, content):
        next_page = '<li class="PartialWebPagination-next">Next</li>'
        pattern = re.compile('<p class="PartialSearchResults-item-url">(.*?\.{domain}).*?</p>'
                             .format(domain=self.target.netloc))
        try:
            links = pattern.findall(content)
            self.find_new_domain = False
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
                        self.find_new_domain = True
        except Exception:
            pass
        if next_page in content:
            # tell engine there still be next page
            return True
        else:
            return False

    def check_response_errors(self,content):
        if not content:
            return [False, ERROR.TIMEOUT]

        if "No results for:" in content:
            return [False,ERROR.END]
        elif "Web Results" in content:
            return [True,0]
        else:
            return [False,ERROR.UNKNOWN]

    def generate_query(self):
        if self.check_max_pageno(): return
        length = len(self.subdomains)

        if length==0:
            query = "site:{domain}".format(domain=self.target.netloc)
            self.queries.append((query,1))
            self.subdomains.update(["www."+self.target.netloc])# 防止 一直请求第一个页面
        elif self.find_new_domain:
            found = ' -site:'.join(list(self.subdomains))
            query = "site:{domain} -site:{found}".format(domain=self.target.netloc, found=found)
            self.queries.append((query, 1))
        else:
            self.queries.append((self.pre_query,self.pre_pageno+1))

    def format_base_url(self, *args):
        return self.base_url.format(query=args[0], page_no=args[1])