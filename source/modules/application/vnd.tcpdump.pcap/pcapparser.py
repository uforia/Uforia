#!/usr/bin/env python

# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the module for handling rfc822 email types

# Do not change from CamelCase because these are the official header names
# TABLE: Date:DATETIME, From:LONGTEXT, SPT:LONGTEXT, To:LONGTEXT, DPT:LONGTEXT, Protocol:LONGTEXT, Data:LONGTEXT

import os,sys,traceback,shutil,recursive,datetime,time,socket,binascii
from dpkt import *

def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath
        assorted = []
        try:
            for timestamp, buffer in pcap.Reader(open(fullpath,'r')):
                timesplit = str(timestamp).split('.')
                firsttimehalf = datetime.datetime.fromtimestamp(int(timesplit[0])).strftime('%Y-%m-%d %H:%M:%S')
                secondtimehalf = timesplit[1]
                microtime = firsttimehalf+'.'+secondtimehalf
                proto = ''
                layer2 = ethernet.Ethernet(buffer)
                if type(layer2) != ethernet.Ethernet:
                    continue
                else:
                    proto += 'ethernet'
                layer3 = layer2.type
                if layer3 != 2048 and layer3 != 34525:
                    continue
                else:
                    if layer3 == 2048:
                        proto += ' ip ipv4'
                    elif layer3 == 34525:
                        proto += ' ip ipv6'
                    else:
                        proto += ' unknown'
                layer4proto = type(layer2.data.data)
                sport,dport,src,dst,payload = None,None,None,None,None
                if layer4proto == udp.UDP:
                    proto   += ' udp'
                    packet  = layer2.data.data
                    sport   = packet.sport
                    dport   = packet.dport
                    src     = socket.inet_ntoa(layer2.data.src)
                    dst     = socket.inet_ntoa(layer2.data.dst)
                    payload = binascii.unhexlify(binascii.b2a_hex(packet.data))
                elif layer4proto == tcp.TCP:
                    proto   += ' tcp'
                    packet  = layer2.data.data
                    sport   = packet.sport
                    dport   = packet.dport
                    src     = socket.inet_ntoa(layer2.data.src)
                    dst     = socket.inet_ntoa(layer2.data.dst)
                    payload = binascii.unhexlify(binascii.b2a_hex(packet.data))
                elif layer4proto == icmp.ICMP:
                    proto   += ' icmp'
                    packet  = layer2.data.data
                    src     = socket.inet_ntoa(layer2.data.src)
                    dst     = socket.inet_ntoa(layer2.data.dst)
                    payload = 'Echo' if packet.data == icmp.ICMP.Echo else 'N/A'
                elif layer4proto == icmp.ICMP6:
                    proto   += ' icmpv6'
                    packet  = layer2.data.data
                    src     = socket.inet_ntoa(layer2.data.src)
                    dst     = socket.inet_ntoa(layer2.data.dst)
                    payload = 'Echo' if packet.data == icmp.ICMP.Echo else 'N/A'
                assorted.append([microtime,src,sport,dst,dport,proto,payload])
            return assorted
        except:
            traceback.print_exc(file=sys.stderr)
            return None
