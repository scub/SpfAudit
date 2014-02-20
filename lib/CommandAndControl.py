#!/usr/bin/python

# Std Lib
from multiprocessing      import Queue, Process
from Queue                import Empty as QueueEmpty
from time                 import sleep

# Custom Libs
from bots.bases           import LoggedBase
from bots.dnsBroker       import dnsBroker 
from lib.types.nameserver import NameServer

class CommandAndControl( LoggedBase ):
    """
        Command And Control
        -------------------

            Acts as an intermediary between all processes,
        managing queues and shared resources. 

    """
    
    def __init__( self, workerCount=3, logPath = 'var/log/gmx_snoop.log' ):
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
            'workers'     : [],
            'workerCount' : int( workerCount ),
            'sql'         : None,
            
            'qin'         : Queue(),
            'qout'        : Queue(),
            'logPath'     : logPath,

            # QUEUE THROTTLING ( 100 * # Workers )
            'throttle'    : int( workerCount ) * 100,
            'targets'     : [],
        }
        
        for i in range( self.state[ 'workerCount' ] ):
            self.addWorker( i + 1 )
            
        self._log( 'init', 'DEBUG', 'Command and control initialized, workers queued and ready for input.' )
        
            
    def __del__( self ):
        """
            Avoiding Cyclic References In Your Design Leads
            to destructors performing admirably.
        """
        for queue in [ 'qin', 'qout' ]:
            self.state[ queue ].cancel_join_thread()
            self.state[ queue ].close()
        
        for worker in self.state[ 'workers' ]:
            worker[ 'proc' ].terminate()
            worker[ 'proc' ].join()
            
        self.state[ 'qin' ]
        
        #print 'Nameserver statistics'
        self.state[ 'nameserver' ].stats()
    
    def addWorker( self, worker_id ):
        """
            Spawn Worker And Add To Workers List
        """
        metaQin, metaQout = Queue(), Queue()
        worker = dnsBroker( workerId   = worker_id,
                            logPath    = self.state[ 'logPath'    ],
                            nameserver = self.state[ 'nameserver' ], 
                            qin        = self.state[ 'qin'        ], 
                            qout       = self.state[ 'qout'       ], 
                            metaQin    = metaQin, 
                            metaQout   = metaQout )
                            
        self.state[ 'workers' ].append( {
            'id'     : worker_id,
            'proc'   : Process( target=worker.background ),
            'worker' : worker,
            'mQin'   : metaQin,
            'mQout'  : metaQout 
        } )

        #self.state[ 'workers' ][-1][ 'proc' ].start()

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

        map( self._flushQueue, [ worker[ 'mQin' ], worker[ 'mQout' ] ] )
            
    def powerWorkforce( self ):
        """
            Start workforce to begin processing queued 
        """
        map( lambda worker: worker[ 'proc' ].start(), self.state[ 'workers' ] )
    
    def cleanupWorkforce( self ):
        """
            Power Down Workforce
        """
        map( self._stopWorker, self.state[ 'workers' ] )
        map( self._flushQueue, [ self.state[ 'qin' ], self.state[ 'qout' ] ] )


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
        
        while stop_count < self.state[ 'workerCount' ]:
            sql_data = self.state[ 'qout' ].get()
                        
            if sql_data.find( "STOP" ) != -1:
                stop_count += 1
                
            #print sql_data
            
        self._log( 'collect', 'DEBUG', 
            'Data harvest completed successfully! <3'
        )
