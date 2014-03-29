#!/usr/bin/python

from Queue                 import Empty as QueueEmpty
from multiprocessing       import Process, Queue
from random                import choice
from time                  import sleep

from lib.CommandAndControl import CommandAndControl as BotMaster
from lib.types.node        import Node


import pdb


def targeting():
    """
        Pull our benchmarking data
    """
    with open( "etc/dom_bench.txt", "r" ) as fd:
        for line in fd:
            yield Node( url = line.strip() )

cnc = BotMaster( workerCount = 1, eBrokerCount = 1, sBrokerCount = 1, logPath = 'var/log/audit_commandAndControl.log', geoipPath = '/usr/share/geoip/GeoLite2-City.mmdb' )

mQin, mQout = cnc.state[ 'workers' ][ 0 ][ 'mQin' ], cnc.state[ 'workers' ][ 0 ][ 'mQout' ]
mQin.put( ( "VERBOSE", None ) ) 


#cnc.pushTargets( targeting )
cnc.powerWorkforce()

# TESTING PAUSE
pdb.set_trace()
cnc.pauseWorkforce()
cnc.pushTargets( targeting )
pdb.set_trace()
cnc.pauseWorkforce()

pdb.set_trace()
while not cnc.state[ 'qin' ].empty():
    try:
        queuedMeta = mQout.get_nowait() 
        print "{}:".format( queuedMeta[0] ),"\n",queuedMeta[1]
    except QueueEmpty as NoMeta:
        continue

cnc.cleanupWorkforce()
