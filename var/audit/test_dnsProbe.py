#!/usr/bin/python

from lib.bots.dnsProbe    import Probe
from lib.types.nameserver import NameServer
from lib.types.node       import Node

x    = Probe( 0, logPath = 'var/log/gmx_snoop.log', nameserver = NameServer() )
host = Node( a_records=['96.126.107.149'] )

# Basic Operation
url = x.resolve_ptr( host )
print url
print x.resolve_mx(  host )
print x.resolve_txt( host )

# Logging
host = Node( a_records=["1.2.3.4"], url = 'darckoncepts.org' )
#url  = x.resolve_ptr( host )
#print url
print x.resolve_mx(  host )
print x.resolve_txt( host )
