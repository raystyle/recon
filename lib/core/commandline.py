#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    
    
    author:  wh1t3P1g <wh1t3P1g@gmail.com>
    description:
    
'''
import argparse


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Recon -- a recon tool')

    cli = parser.add_argument_group('cli')
    cli.add_argument('-u','--url',dest="url",help="setup url to scan")
    cli.add_argument('-f','--file',
                     dest="file",
                     help="setup a file as input")

    cli.add_argument('-o', '--output',
                     dest="output",
                     help="setup output file path")
    cli.add_argument('-p', '--ports',
                     default="small",
                     dest="ports",
                     help="setup ports (small or large)")

    args=parser.parse_args()
    if args.url:
        return args
    if args.file:
        args.url = []
        with open(args.file) as f:
            buf = f.readline()
            while buf:
                if not buf: break
                args.url.append(buf.strip())
                buf = f.readline()
        return args
    print("cmd parse error, try again, python3 recon-cli.py -u domain -o output or -f filepath")
    exit(1)
