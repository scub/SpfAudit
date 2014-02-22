#!/usr/bin/python

from Queue                 import Empty as QueueEmpty
from multiprocessing       import Process, Queue
from random                import choice
from time                  import sleep

from lib.CommandAndControl import CommandAndControl as BotMaster
from lib.types.node        import Node


def targeting():
    for i in range( 125, 200 ):
        yield Node( a_records = [ "96.126.107.{}".format( i ) ] )

cnc = BotMaster( workerCount = 1, logPath = 'var/log/audit_commandAndControl.log', geoipPath = 'etc/GeoLite2-City.mmdb' )

mQin, mQout = cnc.state[ 'workers' ][ 0 ][ 'mQin' ], cnc.state[ 'workers' ][ 0 ][ 'mQout' ]
mQin.put( ( "VERBOSE", None ) ) 

cnc.pushTargets( targeting )
cnc.powerWorkforce()

while not cnc.state[ 'qin' ].empty():
    try:
        queuedMeta = mQout.get_nowait() 
        print queuedMeta
    except QueueEmpty as NoMeta:
        continue

cnc.collect()
cnc.cleanupWorkforce()
