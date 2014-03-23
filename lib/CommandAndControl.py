#!/usr/bin/python

# Std Lib
from multiprocessing      import Queue, Process
from Queue                import Empty as QueueEmpty
from time                 import sleep

# 3rd Party Libs (MaxMind Geoip2) pip install geoip2
from geoip2.database      import Reader

# Custom Bots 
from bots.bases           import LoggedBase
from bots.dnsBroker       import dnsBroker 
from bots.esBroker        import esBroker
from bots.sqlBroker       import sqlBroker

# Custom Types
from lib.types.nameserver import NameServer
from lib.types.node       import Node

class CommandAndControl( LoggedBase ):
    """
        Command And Control
        -------------------

            Acts as an intermediary between all processes,
        managing queues and shared resources. 

        private
        -------
        def _newId( self )
        def _initWorkforce( self )
        def _flushQueue( self, queue )
        def _stopWorker( self, worker )

        public
        ------
        def __init__( self, workerCount, eBrokerCount, sBrokerCount, logPath, geoipPath )
        def __del__( self )
        def powerWorkforce( self )
        def cleanupWorkforce( self )
        def addWorker( self, worker_id )
        def addBroker( self, worker_id, Broker, brokerList, qin )
        def pushTargets( self, target_generator )
        def collect( self )

    """
    def __init__( self, 
                  workerCount  = 3, 
                  eBrokerCount = 3, 
                  sBrokerCount = 1, 
                  logPath      = 'var/log/gmx_snoop.log', 
                  geoipPath    = None,
                  throttle     = 100 ):
        """
            Create new CommandAndControl object.

            @param INT    workerCount - Number of workers to spin up
            @param STRING logPath     - Path to log to
        """

        super( CommandAndControl, self ).__init__( workerId      = 0,
                                                   workerPurpose = 'Command-Control',
                                                   logPath       = logPath )
        
        self.state = {
            # Nameserver
            'nameserver'   : NameServer(),

            # Worker / Broker Lists 
            'esBrokers'    : [],
            'sqlBrokers'   : [],
            'workers'      : [],

            # Worker / Broker Counts 
            'workerCount'  : int( workerCount  ),
            'eBrkrCnt'     : int( eBrokerCount ),
            'sBrkrCnt'     : int( sBrokerCount ),

            # Worker Input Queue
            'qin'          : Queue(),
            # Output Queue To Be Replaced
            'qout'         : Queue(),

            # Worker Sql Broker Queue
            'sqout'        : Queue(),

            # Worker Json Broker Queue
            'eqout'        : Queue(),

            'logPath'      : logPath,

            # QUEUE THROTTLING ( `throttle` * # Workers; Defaults to 100 per worker )
            'throttle'     : int( workerCount ) * throttle,
            'targets'      : [],
            'target_count' : 0,

            # GeoIP Goodies
            'geoip'        : None if geoipPath is None else Reader( geoipPath ),

            # last used id
            'lastId'       : 0,
            'exitQueued'   : False,
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

        # print 'Nameserver statistics'
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
            ( 'workers',    self.state[ 'workerCount' ], self.addWorker, None,                   None      ),
            ( 'sqlBrokers', self.state[ 'sBrkrCnt'    ], self.addBroker, self.state[ 'sqout'  ], sqlBroker ),
            ( 'esBrokers',  self.state[ 'eBrkrCnt'    ], self.addBroker, self.state[ 'eqout'  ], esBroker  ) ]:

            lid        = self.state[ 'lastId' ]
            start, end = lid, count + lid
            for i in range( start, end ):
                if wList == 'workers':
                    SpawnBot( self._newId() ) 
                else:
                    SpawnBot( self._newId(), Broker, wList, queue ) 


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


    def addBroker( self, worker_id, Broker, brokerList, qin ):
        """
            Spawn Broker and add to brokers list
        """
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


    def pollWorkforce( self ):
        """

              Poll workforce to check broker health,
            if found to be finished with processing, then
            fire off event to clean up the rest of the brokers.


        """
        if self.state[ 'exitQueued' ]: return

        # Is there any input left to process?
        if self.state[ 'qin' ].qsize() <= 0:
            # Are our dns brokers still live?
            if all( map( lambda worker: False if worker['proc'].is_alive() else True, self.state[ 'workers' ] ) ):
                # Insert STOP onto queues to stop brokers once complete
                map( self.state[ 'eqout' ].put, [ "STOP" for i in range( self.state[ 'eBrkrCnt' ] + 1 ) ] )
                map( self.state[ 'sqout' ].put, [ "STOP" for i in range( self.state[ 'sBrkrCnt' ] + 1 ) ] )
                self.state[ 'exitQueued' ] = True

    def pushTargets( self, target_generator ):
        """
            Using a generator we feed our host information into 
            the processing queue.

        """
        self.state[ 'target_count' ] = 0
        
        
        for target in target_generator():

            self.state[ 'target_count' ] += 1
            self.state[ 'qin' ].put( target )
            
            # Limit our queue size to `throttle` *  worker count
            # this should reduce our foot print on larger runs
            # considerably
            if self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                self._log( 'pushTargets', 'DEBUG', 'Input Queue Throttle Has Been Triggered' )
            
                while self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                    sleep( 1 )
            
        for worker in range( self.state[ 'workerCount' ] ):
            self.state[ 'qin' ].put( 'STOP' )
        
        self._log( 'pushTargets', 'DEBUG', 
            "Number of targets queued [ {} ] / [ {} ]".format( 
                self.state[ 'qin'          ].qsize(), 
                self.state[ 'target_count' ] 
            )
        )

    def evalGenerator( self, target_generator = None ):
        """
            Using a generator we feed our host information into 
            the processing queue.

            @param str       target_type      - Options include IP/DOMAIN
            @param generator target_generator
        """
        
        for target in target_generator( Node ):

            self.state[ 'target_count' ] += 1
            self.state[ 'qin' ].put( target )
            
            # Limit our queue size to `throttle` *  worker count
            # this should reduce our foot print on larger runs
            # considerably
            if self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                self._log( 'pushTargets', 'DEBUG', 'Input Queue Throttle Has Been Triggered' )
            
                while self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                    sleep( 1 )
            
        self._log( 'pushTargets', 'DEBUG', 
            "Finished queuing target nodes [ {} ] / [ {} ]".format( 
                self.state[ 'qin' ].qsize(), 
                self.state[ 'target_count' ] 
            )
        )
