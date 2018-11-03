#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
from lib.modules.passive.domain import *
from lib.core.common import banner
from lib.core.data import logger
from lib.core.portscan import port_scan
from lib.core.commandline import cmdLineParse
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

def run(target, output, ports):
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
    # port check
    ret = port_scan(list(ret),ports)
    with open(output,"a+") as f:
        ret = "\n".join(ret)
        f.write(ret)
        f.write('\n')

if __name__ == '__main__':

    import uvloop,asyncio
    banner()
    args = cmdLineParse()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    if type(args.url) is list:
        logger.info("check "+str(len(args.url))+" urls")
        for url in args.url:
            run(url,args.output, args.ports)
    else:
        run(args.url, args.output, args.ports)


