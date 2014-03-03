#!/usr/bin/python

# Std Lib
from multiprocessing      import Queue, Process
from Queue                import Empty as QueueEmpty
from time                 import sleep

# 3rd Party Libs (MaxMind Geoip2) pip install geoip2
from geoip2.database      import Reader

# Custom Libs
from bots.bases           import LoggedBase
from bots.dnsBroker       import dnsBroker 
from bots.esBroker        import esBroker
from lib.types.nameserver import NameServer

class CommandAndControl( LoggedBase ):
    
    def __init__( self, 
                  workerCount  = 3, 
                  eBrokerCount = 3, 
                  sBrokerCount = 1, 
                  logPath      = 'var/log/gmx_snoop.log', 
                  geoipPath    = None ):
        """
            Create new CommandAndControl object.

            @param INT    workerCount - Number of workers to spin up
            @param STRING logPath     - Path to log to
        """

        super( CommandAndControl, self ).__init__( workerId      = 0,
                                                   workerPurpose = 'Command-Control',
                                                   logPath       = logPath )
        
        self.state = {
            'nameserver'  : NameServer(),

            # Worker / Broker Lists 
            'esBrokers'   : [],
            'sqlBrokers'  : [],
            'workers'     : [],

            # Worker / Broker Counts 
            'workerCount' : int( workerCount  ),
            'eBrkrCnt'    : int( eBrokerCount ),
            'sBrkrCnt'    : int( sBrokerCount ),

            # Worker Input Queue
            'qin'         : Queue(),
            # Output Queue To Be Replaced
            'qout'        : Queue(),

            # Worker Sql Broker Queue
            'sqout'       : Queue(),

            # Worker Json Broker Queue
            'eqout'       : Queue(),

            'logPath'     : logPath,

            # QUEUE THROTTLING ( 100 * # Workers )
            'throttle'    : int( workerCount ) * 100,
            'targets'     : [],

            # GeoIP Goodies
            'geoip'       : None if geoipPath is None else Reader( geoipPath ),

            # last used id
            'lastId'      : 0,
        }

        self._initWorkforce()


        self._log( 'init', 'DEBUG', 'Command and control initialized, workers queued and ready for input.' )
        
            
    def __del__( self ):
        """
            Avoiding Cyclic References In Your Design Leads
            to destructors performing admirably.
        """
        # Stop Workers
        for workerList in [ self.state[ i ] for i in [ 'workers', 
                                                       'sqlBrokers', 
                                                       'esBrokers' ] ]:
            map( self._stopWorker, self.state[ workerList ] ) 

        # Flush Queues
        map( self._flushQueue, 
             [ self.state[ queue ] for queue in [ 'qin',
                                                  'qout',
                                                  'sqout', 
                                                  'eqout' ] ] )

        #print 'Nameserver statistics'
        self.state[ 'nameserver' ].stats()
    
    def _newId( self ):
        """
            Return new id, and increment id counter 

               We start our Id's at one to account
            for command and control being worker 0

        """
        self.state[ 'lastId' ] += 1
        return self.state[ 'lastId' ]

    def _initWorkforce( self ):

        """
            Initialize Workers And Brokers
        """

        for ( wList, count, SpawnBot, queue, Broker ) in [ 
            ( 'workers',    self.state[ 'workerCount' ], self.addWorker, None,                  None      ),
            #( 'sqlBrokers', self.state[ 'eBrkrCnt'    ], self.addBroker, self.state[ 'sqout' ], sqlBroker ),
            ( 'esBrokers',  self.state[ 'sBrkrCnt'    ], self.addBroker, self.state[ 'eqout'  ], esBroker  ) ]:

            lid        = self.state[ 'lastId' ]
            start, end = lid, count + lid
            for i in range( start, end ):
                if wList != 'workers':
                    SpawnBot( self._newId(), Broker, wList, queue ) 
                else:
                    SpawnBot( self._newId() ) 


    def addWorker( self, worker_id ):
        """
            Spawn Worker And Add To Workers List
        """
        metaQin, metaQout = Queue(), Queue()
        worker = dnsBroker( workerId   = worker_id,
                            logPath    = self.state[ 'logPath'    ],
                            nameserver = self.state[ 'nameserver' ], 
                            geoip      = self.state[ 'geoip'      ], 
                            qin        = self.state[ 'qin'        ], 
                            #qout       = self.state[ 'qout'       ], 
                            sqout      = self.state[ 'sqout'      ],
                            eqout      = self.state[ 'eqout'      ],
                            metaQin    = metaQin, 
                            metaQout   = metaQout )
                            
                            
        self.state[ 'workers' ].append( {
            'id'     : worker_id,
            'proc'   : Process( target=worker.background ),
            'worker' : worker,
            'mQin'   : metaQin,
            'mQout'  : metaQout,
        } )

        #self.state[ 'workers' ][-1][ 'proc' ].start()

    def addBroker( self, worker_id, Broker, brokerList, qin ):
        """
            Spawn Broker and add to brokers list
        """
        #import pdb; pdb.set_trace()
        metaQin, metaQout = Queue(), Queue()

        broker = Broker( workerId = worker_id, 
                         logPath  = self.state[ 'logPath' ],
                         qin      = qin,  
                         metaQin  = metaQin,
                         metaQout = metaQout,
                         geoip    = self.state[ 'geoip' ] )

        self.state[ brokerList ].append( {
            'id'     : worker_id,
            'proc'   : Process( target=broker.background ),
            'broker' : broker,
            'mQin'   : metaQin,
            'mQout'  : metaQout,
        } )

    def _flushQueue( self, queue ):
        """
            Flush all remnants left in queue, then close
        """
        while not queue.empty():
            try:
                queue.get_nowait()
            except QueueEmpty as FinishedFlushing:
                break

        return queue.close()

    def _stopWorker( self, worker ):
        """
            Stop a given worker
        """
        worker[ 'proc' ].terminate()
        worker[ 'proc' ].join()

        map( self._flushQueue, [ worker[ i ] for i in [ 'mQin', 'mQout' ] ] )
            
    def powerWorkforce( self ):
        """
            Start workforce to begin processing queued 

        """
        for workerList in [ self.state[ i ] for i in [ 'workers', 
                                                       'sqlBrokers', 
                                                       'esBrokers' ] ]:
 
            map( lambda worker: worker[ 'proc' ].start(), workerList )

    
    def cleanupWorkforce( self ):
        """

            Power Down Workforce

        """
        for workerList in [ self.state[ i ] for i in [ 'workers', 
                                                       'sqlBrokers', 
                                                       'esBrokers' ] ]:
            map( self._stopWorker, workerList )

        map( self._flushQueue, 
             [ self.state[ i ] for i in [ 'qin', 'sqout', 'eqout' ] ] )

    def pushTargets( self, target_generator ):
        """
            Using a generator we feed our host information into 
            the processing queue.

        """
        self.state[ 'target_count' ] = 0
        
        
        for target in target_generator():

            #self.state[ 'targets' ].append( target )
            self.state[ 'target_count' ] += 1
            self.state[ 'qin' ].put( target )
            
            # Limit our queue size to 100 times our worker count
            # this should reduce our foot print on larger runs
            # considerably
            
            if self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                self._log( 'pushTargets', 'DEBUG', 'Input Queue Throttle Has Been Triggered' )
            
                while self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                    sleep( 1 )
            
        for worker in range( self.state[ 'workerCount' ] ):
            self.state[ 'qin' ].put( 'STOP' )
        
        self._log( 'pushTargets', 'DEBUG', 
            "Number of targets queued [ {} ] / [ {} ]".format( self.state[ 'qin' ].qsize(), self.state[ 'target_count' ] )
        )
                                                              
        
    def collect( self ):
        stop_count = 0
        
        self._log( 'collect', 'DEBUG', 
                   'Data Harvest Begins, Input Queue Size [ {} ]'.format( self.state[ 'qin' ].qsize() ) )
            
        while not self.state[ 'qin' ].empty():
            self._log( 'collect', 'DEBUG', 
                       'Collection paused while probes working [ {} ]'.format( self.state[ 'qin' ].qsize() ) )

            sleep( self.state[ 'qin' ].qsize() )
        
        while not self.state[ 'sqout' ].empty():
            node = self.state[ 'sqout' ].get()
                        
            if type( node ) != str:
                if all( map( lambda x: x is not None, [ node.url, node.a_records, node.mx_records ] ) ):
                    print node
            
        self._log( 'collect', 'DEBUG', 
            'Data harvest completed successfully! <3'
        )

