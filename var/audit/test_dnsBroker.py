#!/usr/bin/python

from Queue                import Empty as QueueEmpty
from multiprocessing      import Queue
from random               import choice

from geoip2.database      import Reader

from lib.types.nameserver import NameServer 
from lib.types.node       import Node
from lib.bots.dnsBroker   import dnsBroker 

qin, qout, metaQin, metaQout = Queue(), Queue(), Queue(), Queue()

geoip = Reader( 'etc/GeoLite2-City.mmdb' )

# Queue Meta Requests 
metaQin.put( ( 'VERBOSE', None ) )
metaQin.put( ( 'NOP',     None ) )
metaQin.put( ( 'NOP',     None ) )
metaQin.put( ( 'NOP',     None ) )

# Push Targets into queue
for i in range( 5, 10 ): 
    node = Node( a_records = ["96.126.107.14{}".format( i ),] )
    qin.put( node )
qin.put( "STOP" )

x = dnsBroker( 0, 'var/log/testDBroker.log', NameServer(), qin = qin, qout = qout, metaQin = metaQin, metaQout = metaQout, geoip = geoip )

x.background()

while qout.qsize() > 0:
    try:
        out = qout.get()
        if "STOP" not in out:
            print out
        else:
            break
    except QueueEmpty as FinishedProcessing:
        break

# Flush Queues
for k, q in [ ( 'qin', qin ), ( 'qout', qout ), ( 'mQin', metaQin ), ( 'mQout', metaQout ) ]:
    while q.empty() == False:
        print "[{}] Remnants: {}".format( k, q.get_nowait() )
    q.close()