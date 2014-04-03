#!/usr/bin/python

# Std Lib
from socket               import socket, SOCK_STREAM, AF_INET, timeout as SOCKET_TIMEOUT
from socket               import error as SOCKET_ERROR
from Queue                import Empty as QueueEmpty
from multiprocessing      import Queue, Process
from datetime             import datetime
from time                 import sleep
from random               import choice

# 3rd Party Libs (MaxMind Geoip2) pip install geoip2
from geoip2.database      import Reader

# Custom Bots 
from bots.bases           import LoggedBase
from bots.dnsBroker       import dnsBroker 
from bots.esBroker        import esBroker
from bots.sqlBroker       import sqlBroker
from bots.mxBroker        import mxBroker

# Custom Types
from types.nameserver import NameServer
from types.node       import Node

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
                  mBrokerCount = 1,
                  logPath      = 'var/log/gmx_snoop.log', 
                  geoipPath    = None,
                  throttle     = 100 ):
        """
            Create new CommandAndControl object.

            @param INT    workerCount  - Number of workers to spin up
            @param INT    eBrokerCount - Number of Json brokers to spin 
            @param INT    sBrokerCount - Number of Sql Brokers to spin 
            @param INT    mBrokerCount - Number of MX Brokers to spin 
            @param STRING logPath      - Path to log to
            @param STRING geoipPath    - Path to geoip database
            @param INT    throttle     - Throttle seed, value becomes throttle * workerCount
        """

        super( CommandAndControl, self ).__init__( workerId      = 0,
                                                   workerPurpose = 'Command-Control',
                                                   logPath       = logPath )
        
        self.state = {
            # Nameserver
            'nameserver'    : NameServer(),

            # Worker / Broker Lists 
            'mxBrokers'     : [],
            'esBrokers'     : [],
            'sqlBrokers'    : [],
            'workers'       : [],
            'CnCAuxiliary'  : [],

            # Worker / Broker Counts 
            'workerCount'   : int( workerCount  ),
            'eBrkrCnt'      : int( eBrokerCount ),
            'sBrkrCnt'      : int( sBrokerCount ),
            'mBrkrCnt'      : int( mBrokerCount ),

            # Worker I/O Queues
            'qin'           : Queue(),
            'qout'          : Queue(),

            # Sql Broker Queue
            'sqout'         : Queue(),

            # Json Broker Queue
            'eqout'         : Queue(),

            # MX Broker Queue
            'mqout'         : Queue(),

            # Logging Path
            'logPath'       : logPath,

            # QUEUE THROTTLING ( `throttle` * # Workers; Defaults to 100 per worker )
            'throttle'      : int( workerCount ) * throttle,
            'targets'       : [],
            'target_count'  : 0,

            # GeoIP Goodies
            'geoip'         : None if geoipPath is None else Reader( geoipPath ),

            # last used id
            'lastId'        : 0,
            'exitQueued'    : False,
            'botsPaused'    : True,
            'lastTCheck'    : None,

            # Application Layer Connection Polling
            # root is not always an option. 
            # (HTTP traffic is begnign enough)
            'conPoll'       : [
                "74.125.239.132",
                "74.125.239.131",
                "74.125.239.136",
                "74.125.239.137",
                "74.125.239.130",
                "74.125.239.129",
                "74.125.239.133",
                "74.125.239.134",
                "74.125.239.128",
                "74.125.239.142",
                "74.125.239.135",
            ], #P.S: Thanks Again Mister Googles <3


        }

        self._initWorkforce()

        self._log( 'init', 'DEBUG', 'Command and control initialized, workers queued and ready for input.' )
        
            
    def __del__( self ):
        """
            Avoiding Cyclic References In Your Design Leads
            to destructors performing admirably.
        """
        # Stop Workers
        self.stopWorkforce()

        # Stop Auxiliary Workers
        map( self._stopWorker, self.state[ 'CnCAuxiliary' ] )

        # Flush Queues
        map( self._flushQueue, 
             [ self.state[ queue ] for queue in [ 'qin',
                                                  'qout',
                                                  'sqout', 
                                                  'eqout',
                                                  'mqout'  ] ] )
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
            ( 'esBrokers',  self.state[ 'eBrkrCnt'    ], self.addBroker, self.state[ 'eqout'  ], esBroker  ),
            ( 'mxBrokers',  self.state[ 'mBrkrCnt'    ], self.addBroker, self.state[ 'mqout'  ], mxBroker  ) ]:

            lid        = self.state[ 'lastId' ]
            start, end = lid, count + lid
            for i in range( start, end ):
                if wList == 'workers':
                    SpawnBot( self._newId() ) 
                else:
                    SpawnBot( self._newId(), Broker, wList, queue ) 

        self.state[ 'exitQueued' ] = False

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
                            mqout      = self.state[ 'mqout'      ],
                            metaQin    = metaQin, 
                            metaQout   = metaQout )
                            
                            
        self.state[ 'workers' ].append( {
            'id'     : worker_id,
            'proc'   : Process( 
                name   = "{}.{}".format( 
                    'dnsBroker', 
                    str( worker_id )
                ),
                target = worker.background 
            ),
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
            'proc'   : Process( 
                name   = "{}.{}".format( 
                    brokerList,
                    str( worker_id )
                ),
                target = broker.background 
            ),
            'broker' : broker,
            'mQin'   : metaQin,
            'mQout'  : metaQout,
        } )

    def _flushQueue( self, queue ):
        """
            Flush all remnants left in queue, then close
        """
        if queue is None: return

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
            
    def pauseWorkforce( self ):
        """
            Pause/Continue worker processing
        """
        if self.state[ 'botsPaused' ]:
            self._initWorkforce()
            self.powerWorkforce()
            return 'RESUMED'
        else:
            self.stopWorkforce()
            return 'PAUSED'

    def stopWorkforce( self ):
        """
            Stop workforce
        """
        # Stop Workers
        for workerList in [ self.state[ i ] for i in [ 'workers', 
                                                       'sqlBrokers', 
                                                       'esBrokers',
                                                       'mxBrokers'   ] ]:
            map( self._stopWorker, workerList ) 
            del workerList[:]

        self.state[ 'botsPaused' ] = True 

    def powerWorkforce( self ):
        """
            Start workforce to begin processing queued 

        """
        for workerList in [ self.state[ i ] for i in [ 'workers', 
                                                       'sqlBrokers', 
                                                       'esBrokers',
                                                       'mxBrokers'   ] ]:
 
            map( lambda worker: worker[ 'proc' ].start(), workerList )

        self.state[ 'botsPaused' ] = False
    
    def cleanupWorkforce( self ):
        """

            Power Down Workforce

        """
        self.stopWorkforce()

        map( self._flushQueue, 
             [ self.state[ i ] for i in [ 'qin', 'sqout', 'eqout', 'mqout' ] ] )


    def pollWorkforce( self ):
        """

              Poll workforce to check broker health,
            if found to be finished with processing, then
            fire off event to clean up the rest of the brokers.


        """
        if self.state[ 'exitQueued' ]: return


        # Check auxiliary processes
        finishedWorkers = []
        for i in range( len( self.state[ 'CnCAuxiliary' ] ) ):
            bot = self.state[ 'CnCAuxiliary' ][ i ]

            if not bot[ 'proc' ].is_alive():
                #self.state[ 'CnCAuxiliary' ].pop( i )
                bot[ 'proc' ].terminate()
                bot[ 'proc' ].join()
                finishedWorkers.append( bot )

        for bot in finishedWorkers:
            self.state[ 'CnCAuxiliary' ].remove( bot )

        # Is there any input left to process?
        if self.state[ 'qin' ].qsize() <= 0:
            # Are our dns brokers still live?
            if all( map( lambda worker: False if worker['proc'].is_alive() else True, self.state[ 'workers' ] ) ):
                # Insert STOP onto queues to stop brokers once complete
                map( self.state[ 'eqout' ].put, [ "STOP" for i in range( self.state[ 'eBrkrCnt' ] + 1 ) ] )
                map( self.state[ 'sqout' ].put, [ "STOP" for i in range( self.state[ 'sBrkrCnt' ] + 1 ) ] )
                map( self.state[ 'mqout' ].put, [ "STOP" for i in range( self.state[ 'mBrkrCnt' ] + 1 ) ] )
                self.state[ 'exitQueued' ] = True

    def pushTargets( self, target_generator ):
        """
            Using a generator we feed our host information into 
            the processing queue.

        """

        worker_id   = self._newId()
        worker_proc = Process(
            target = self.evalGenerator, 
            name   = "TargetGenerator.{}".format( 
                str( worker_id )
            ),
            kwargs = {
                'generator' : target_generator,    
            }
        )
         
        self.state[ 'CnCAuxiliary'  ].append( {
            'id'    : worker_id, 
            'proc'  : worker_proc, 
            'mQin'  : None,
            'mQout' : None,
        } )

        self.state[ 'target_count' ] = 0
        worker_proc.start()
        
    def evalGenerator( self, **kwargs ): 
        """
            Using a generator we feed our host information into 
            the processing queue.

            @param str       target_type      - Options include IP/DOMAIN
            @param generator target_generator
        """
        
        for target in kwargs[ 'generator' ]( Node ):

            if target is None: break 

            self.state[ 'qin'          ].put( target )
            self.state[ 'target_count' ] += 1
            
            # Limit our queue size to `throttle` *  worker count
            # this should reduce our foot print on larger runs
            # considerably
            if self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                while self.state[ 'qin' ].qsize() >= self.state[ 'throttle' ]:
                    sleep( 1 )
            
        self._log( 'evalGenerator', 'DEBUG', 
            "Finished queuing target nodes [ {} ] / [ {} ]".format( 
                self.state[ 'qin' ].qsize(), 
                self.state[ 'target_count' ] 
            )
        )

    def checkConnection( self ):
        """
                Check connection integrity to make sure we 
            still have a valid connection, if not all bots
            should be paused until we can obtain a connection.
            Because icmp requires raw sockets, and raw sockets
            require root, we use an application layer check to
            keep the protocols begnign. By completing the handshake
            we can be sure connection remains intact.

            @return BOOL True  - Connection Integrity Remains
                         False - Connection Failed, Pause Workers 
        """
        sock = socket( AF_INET, SOCK_STREAM )

        try:
            sock.connect(( choice( self.state[ 'conPoll' ] ), 80 ) )
        except SOCKET_ERROR:
            return False
        return True

    def connectionPoll( self, interval = 5 ):
        """
              check the connection over a given interval
            pausing/continuing workforce as the need
            arises.

            @param INT interval - time in minutes to check connection 
            
        """
        if self.state[ 'lastTCheck' ] is None:
            self.state[ 'lastTCheck' ] = datetime.now()
        elif ( datetime.now() - self.state[ 'lastTCheck' ] ).seconds < interval * 60:
            return

        if not self.checkConnection():
            if not self.state[ 'botsPaused' ]:
               self.pauseWorkforce()

               while not self.connectionPoll():
                   self._nap()

               self.pauseWorkforce()
