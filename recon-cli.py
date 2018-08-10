#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain import *
from lib.core.common import banner
from lib.core.data import logger
engines = {
    'baidu': BaiduEngine,
    'ask': AskEngine,
    'bing': BingEngine,
    'ssl': CrtSearchEngine,
    'yahoo': YahooEngine,
    'dnsdumpster': DNSdumpsterEngine,
    'netcraft': NetcraftEngine,
    'threatcrowd': ThreatCrowdEngine,
    'virustotal': VirustotalEngine,
    'bugscanner': BugscannerEngine,
    'chinaz': ChinazEngine,
}

def run(target):
    used_engine = [_(target) for _ in engines.values()]
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    tasks = []
    for engine in used_engine:
        tasks.append(asyncio.ensure_future(engine.run()))

    for task in tasks:
        loop.run_until_complete(task)
    loop.close()
    ret = set()
    for engine in used_engine:
        ret.update(engine.subdomains)
    print(ret)
    print(len(ret))
if __name__ == '__main__':

    import uvloop,asyncio,sys
    banner()
    args = sys.argv
    if len(args)!=2:
        logger.error("use python3 recon-cli.py domain")
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        run(args[1])


