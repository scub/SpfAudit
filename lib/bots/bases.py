#!/usr/bin/python

from    Queue           import Empty as QueueEmpty
from    multiprocessing import Queue
from    time            import sleep
from    datetime        import datetime
import  logging

LOGLEVEL = logging.NOTSET

class LoggedBase( object ):
    """
            Base class provides centralized logging and meta procressing 
        facilities for all derived objects.

    """

    def __init__( self, workerId = None, workerPurpose = None, logPath = None, **kwargs  ):
        """
                Create LoggedBase object to centralize logging 
            and meta request processing.

            @param int        workerId      - Worker Id
            @param STRING     workerPurpose - Worker Purpose, Used to create logging handler
            @param String     logPath       - Path to log to
            @param DICT       **kwargs      - If extending class requires more meta information, 
                                              it can be fed through here as a dictionary; 
                                              (Unrequired under normal operation; Likely to be purged)

            @return LoggedBase()
        """

        super( LoggedBase, self ).__init__()

        self.meta = {
            # Log Path
            'logPath' : logPath,

            # Logging Vector
            'logging' : logging,

            # Bot Id
            'id'      : workerId,

            # Processed Records
            'rcnt'    : 0,

            # Last Record Processed
            'lrcd'    : 0,

            # Verbosity ( Used Within Menu System )
            'verbose' : False,

            # Bot Purpose
            'purpose'  : workerPurpose,

            # Last Record Number Procesed
            'lrcnt'    : 0,

            # Nap Weight
            'deltaL'   : None,
        }

        # Stats Fed By Menu System
        self.stats = {
            # All Bot Statistics
            'ALL'     : lambda x: "[{}-{}] Total Records Processed [ {} ] Last Processed [ {} ]".format( 
                self.meta[ 'purpose' ],
                self.meta[ 'id'      ],
                self.meta[ 'rcnt'    ],                                                                                         
                self.meta[ 'lrcd'    ] 
            ),

            # Last Processed Record
            'LPROC'   : lambda x: "[{}-{}] Last Processed Record [ {} ]".format( 
                self.meta[ 'purpose' ],                                                                 
                self.meta[ 'id'      ],
                self.meta[ 'lrcd'    ] 
            ),

            # Incremental Updates
            'INC'     : self._displayIncremental,

            # Trigger Verbosity
            'VERBOSE' : self._setVerbose, 


            # Observer Exiting Flush Any Verbosity
            'XOBSRV'  : self._flushVerbosity, 
        }

        # Add any additional parameters
        if kwargs is not None:
            for key, value in kwargs.iteritems():
                self.meta[ key ] = value

        # Centralize Logging Facilities For All Processes
        logging.basicConfig( 
            format   = '%(asctime)s %(levelname)s [%(name)s]: %(message)s',
            level    = logging.NOTSET,
            filename = self.meta[ 'logPath' ], 
            datefmt  = '%d-%m-%Y %H:%M:%S' 
        )

        # Minimize elasticsearch/urllib3 spam 
        for spammers in [ 'elasticsearch', 'elasticsearch.trace', 'urllib3.connectionpool' ]:
            logging.getLogger( spammers ).setLevel( 
                logging.CRITICAL
            )

    def _log( self, handler, log_level, message ):
        """
             Emit message to handler, using appropriate identifier for bot purpose.

            @param String handler     - Handler ID
            @param String log_level   - String Log Level To Log Event Under
                                        available options: critical, error,
                                        warning, debug.
            @message                  - String Event to be logging
        """

        logHandler = "{}{}.{}".format( self.meta[ 'purpose' ], self.meta[ 'id' ], handler )
        logger     = self.meta[ 'logging' ].getLogger( logHandler )
        
        log_event = {
            'critical' : { 'level' : logging.CRITICAL, 'callback' : logger.critical },
            'error'    : { 'level' : logging.ERROR,    'callback' : logger.error    },
            'warning'  : { 'level' : logging.WARNING,  'callback' : logger.warning  },
            'info'     : { 'level' : logging.INFO,     'callback' : logger.info     },
            'debug'    : { 'level' : logging.DEBUG,    'callback' : logger.debug    },
        }

        if logger.isEnabledFor( log_event[ log_level.lower() ][ 'level' ] ): 
            log_event[ log_level.lower() ][ 'callback' ]( message )


    def _processMeta( self, metaQin, metaQout ):
        """
               Process Queued meta requests, and push
            the results through the output queue.

            @param Queue metaQin   - Input Queue
            @param Queue metaQout  - Output Queue

        """
        if self.meta[ 'verbose' ]:
            self._displayIncremental( metaQout ) 

        try:
            query = metaQin.get_nowait()

            if self.stats.has_key( query[ 0 ] ):
                metaQout.put( self.stats[ query[ 0 ] ]( query[ 1 ] ) )

        except QueueEmpty as NoMetaRequests:
            pass

    def _displayIncremental( self, metaQout ):
        """
              Display records inrementally, performing
            minor sanity checks to make sure we aren't
            displaying the same record again; Added
            Stipulation of turning off verbosity
            
            @param Queue metaQout   - Output Queue For Bot I/O
        """
        output = [ "[{}-{}]:".format( 
            self.meta[ 'purpose' ], self.meta[ 'id' ]
        ) ]

        if self.meta[ 'lrcnt' ] != self.meta[ 'rcnt' ]:
            self.meta[ 'lrcnt' ] = self.meta[ 'rcnt' ]

            output.append( "{}) {}".format( 
                self.meta[ 'rcnt'    ],
                self.meta[ 'lrcd'    ] ) 
            )
        else:
            output.append( "No records to process, turning off verbosity." )
            self._setVerbose( None )

        metaQout.put( ( "DATA", ' '.join( output ) ) ) 

    def _setVerbose( self, args, **kwargs ):
        """
            Trigger Verbosity Setting 

            @param list args    - Templated Function Provides Buffer For Arbitrary Arguments
            @param dict kwargs  - Templated Function Provides Hashtable For Arbitrary Arguments
        """
        self.meta[ 'verbose' ] = True if self.meta[ 'verbose' ] is False else False
        return "[{}-{}]: Set Verbosity To {}.".format( self.meta[ 'purpose' ], self.meta[ 'id' ], self.meta[ 'verbose' ] )

    def _flushVerbosity( self, args, **kwargs ):
        """
            Flush Verbose state, called by XOBSRV

            @param list args    - Templated Function Provides Buffer For Arbitrary Arguments
            @param dict kwargs  - Templated Function Provides Hashtable For Arbitrary Arguments
        """
        self.meta[ 'verbose' ] = False
        return "[{}-{}]: Flushed Observable State.".format( self.meta[ 'purpose' ], self.meta[ 'id' ] )

    def _nap( self ):
        """
                Nap scales based on number of 
            seconds since last processed record.

        """
        ( curDelta, napTime ) = ( datetime.now(), 1 )

        deltaT                = curDelta - self.meta[ 'deltaL' ] 

        if deltaT.seconds < 1:
            pass 
        elif deltaT.seconds < 90:
            napTime = deltaT.seconds
        else:
            napTime = self.meta[ 'maxNap' ]

        sleep( napTime )
