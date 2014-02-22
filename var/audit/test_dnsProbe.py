#!/usr/bin/python

from geoip2.database      import Reader

from lib.bots.dnsProbe    import Probe
from lib.types.nameserver import NameServer
from lib.types.node       import Node


geoip = Reader( 'etc/GeoLite2-City.mmdb' ) 

x     = Probe( 0, logPath = 'var/log/gmx_snoop.log', nameserver = NameServer() )
host  = Node( a_records=['96.126.107.149'] )

# Basic Operation
url = x.resolve_ptr( host )
x.resolve_mx(  host )
x.resolve_txt( host )
x.pull_geoip( host, geoip )
print '\n\nNode( {} ):'.format( host.url )
for k, v in host.convert( 'json' ).iteritems():
    print "\t{} => {}".format( k, v )

del host

# Logging
host = Node( a_records=["1.2.3.4"], url = 'darckoncepts.org' )
#url  = x.resolve_ptr( host )
#print url
x.resolve_mx(  host )
x.resolve_txt( host )
print '\n\nNode( {} ):'.format( host.url )
for k, v in host.convert( 'json', geoip ).iteritems():
    print "\t{} => {}".format( k, v )
print "\n"
