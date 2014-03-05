#!/usr/bin/python

from Queue import Empty      as QueueEmpty
from bases import LoggedBase
from time  import sleep

class brokerBase( LoggedBase ):

    def __init__( self, workerId = None, workerPurpose = None, logPath = None, qin = None, metaQin = None, metaQout = None ):

        super( brokerBase, self ).__init__( workerId      = workerId,
                                            workerPurpose = workerPurpose,
                                            logPath       = logPath )

        self.state = {
            'id'    : workerId,
            'qin'   : qin,
            'mQout' : metaQout,
            'mQin'  : metaQin,
            'alive' : True,
        }

    def process( self, node ):
        """
            Abstract Method, Process A Given Record 
        """
        pass

    def bootstrap( self ):
        """
            Abstract method, provides foothold to bootstrap broker
        """
        pass

    def background( self ):
        """
            Using queues have broker run unhindered, without the requirement
            of manually specifying individual host addresses. Designed to be
            used in tandem with multiprocessing.Process()

        """
        # Bootstrap broker if required
        self.bootstrap()

        while self.state[ 'alive' ]:

            self._processMeta( self.state[ 'mQin' ], self.state[ 'mQout' ] )

            try:
                NodeObj = self.state[ 'qin' ].get_nowait()
            except QueueEmpty as AwaitingData:
                #sleep( 1 ) < integrate scaling nap() in logged base, replace all instances of sleep()
                continue
            except StopIteration as StopProcessing:
                self.state[ 'alive' ] = false
                continue

            # Check That We Are A Node Object
            if type( NodeObj ) != str:

                # Buffer Last Record
                self.meta[ 'lrcd' ] = NodeObj
                
                # Process Node Object
                self.process( NodeObj )

                # Increment Record Counter
                self.meta[ 'rcnt' ] += 1

            else:
                self._log( 'background', "DEBUG", "Stop triggered." )
                self.state[ 'alive' ] = False
                break

        self._log( 'background', 'DEBUG', 'Execution Complete.' )
