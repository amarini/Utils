#!/usr/bin/env python

#import os,sys
from subprocess import call, check_output
import re
import threading
import time

from optparse import OptionParser, OptionGroup

usage = "usage: %prog [options] exe1 exe2 ..."
parser=OptionParser(usage=usage)
#parser.add_option("-n","--nserver" ,dest='nserver',type='int',help="Number of server to use [Default=%default]",default=10)
parser.add_option("-c","--command" ,dest='cmd',type='string',help="Try to run a cmd [Default=%default]",default="")
(opts,args)=parser.parse_args()

def scout():
	''' scout lxplus servers '''
	servers={}
	host = "host lxplus.cern.ch | grep 'has address' | cut -d' ' -f 4 | while read ip ; do host $ip | sed 's/.*pointer //' | sed 's/\.$//'; done "
	hosts = check_output(host, shell=True)
	for l in hosts.split():
		servers[ l ] = 0
	return servers
def PrintServers(servers):
	print "I found the following lxplus:"
	for s in servers:
		print "\t*",s
	print "I found ", len(servers), "servers"

servers=scout()

PrintServers(servers)
raw_input("Is ok?")

if opts.cmd != "":
  for server in servers:
     cmd = "ssh "+ server  + ' "' + opts.cmd + '"'
     print "---- " + server + " -----"
     call(cmd,shell=True)
     print "-------------------------"


