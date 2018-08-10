#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
import re
from urllib import parse as urlparse
from lib.core.exceptions import ReconInvalidURLException
from lib.core.enums import UA,default_headers
import random,string
from dns import resolver

def generate_random_str(size,chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def check_domain(url):
    """
    check domain
    valid domain: http://example.com or https://example.com or example.com
    :param url:
    :return:
    """
    pattern = re.compile("^(http://|https://)?[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$")
    if not pattern.match(url):
        raise ReconInvalidURLException # a critical error

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    return urlparse.urlparse(url)

def is_extensive_domain(url):
    """
    judge url whether or not an extensive domain
    :param url: url parser
    :return: boolean
    """
    random_subdomains = [ generate_random_str(12)+'.'+url.netloc for _ in range(3)]
    times=0
    rs = resolver.Resolver()
    rs.timeout = 1
    rs.nameservers = ['114.114.114.114','8.8.8.8']
    addresses = []
    for domain in random_subdomains:
        try:
            answers = rs.query(domain,'A')
            addresses.append(answers[0].address) # fetch the first IP
        except resolver.NXDOMAIN:
            # if times == 3, this domain is not an extensive domain
            times+=1
            print("cannot fetch {domain} A record".format(domain=domain))
    if times==3:
        return False
    elif times<3 and len(addresses) > 0 and addresses[0] not in addresses[1:]:
        return False
    else:
        return True

def random_ua():
    tmp = default_headers
    tmp['User-Agent'] = UA[random.randint(0,6)]
    return tmp

def banner():
    pic = """
 ______    _______  _______  _______  __    _ 
|    _ |  |       ||       ||       ||  |  | |
|   | ||  |    ___||       ||   _   ||   |_| |
|   |_||_ |   |___ |       ||  | |  ||       |
|    __  ||    ___||      _||  |_|  ||  _    |
|   |  | ||   |___ |     |_ |       || | |   |
|___|  |_||_______||_______||_______||_|  |__|

    author: @wh1t3p1g       version: 0.0.1
"""
    print(pic)
if __name__ == '__main__':
    banner()
