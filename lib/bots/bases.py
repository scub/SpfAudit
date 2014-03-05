#!/usr/bin/python

from    Queue           import Empty as QueueEmpty
from    multiprocessing import Queue
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

        import logging

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

        }

        # Stats Used By Menu System
        self.stats = {
            # All Bot Statistics
            'ALL'     : lambda x: "[{}-{}] Total Records Processed [ {} ] Last Processed [ {} ]".format( self.meta[ 'purpose' ],
                                                                                                         self.meta[ 'id'      ],
                                                                                                         self.meta[ 'rcnt'    ],
                                                                                                         self.meta[ 'lrcd'    ] ),

            # Last Processed Record
            'LPROC'   : lambda x: "[{}-{}] Last Processed Record [ {} ]".format( self.meta[ 'purpose' ],
                                                                                 self.meta[ 'id'      ],
                                                                                 self.meta[ 'lrcd'    ] ),


            # Incremental Updates
            'INC'     : lambda x: "[{}-{}]: {}) {}".format( self.meta[ 'purpose' ],
                                                            self.meta[ 'id'      ],
                                                            self.meta[ 'rcnt'    ],
                                                            self.meta[ 'lrcd'    ] ),

            # Trigger Verbosity
            'VERBOSE' : self._setVerbose, 


            # Observer Exiting Flush Any Verbosity
            'XOBSRV'  : self._flushVerbosity, 
        }

        # Add any additional parameters
        if kwargs is not None:
            for key, value in kwargs.iteritems():
                self.meta[ key ] = value

        # Logging Facilities For All Processes
        logging.basicConfig( format   = '%(asctime)s %(levelname)s [%(name)s]: %(message)s',
                             level    = logging.NOTSET,
                             filename = self.meta[ 'logPath' ], 
                             datefmt  = '%d-%m-%Y %H:%M:%S' )


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
            metaQout.put( ( "DATA", self.stats[ "INC" ]( None ) ) )

        try:
            query = metaQin.get_nowait()

            if self.stats.has_key( query[ 0 ] ):
                metaQout.put( ( "DATA", self.stats[ query[ 0 ] ]( query[ 1 ] ) ) )

        except QueueEmpty as NoMetaRequests:
            pass

    def _setVerbose( self, args, **kwargs ):
        """
            Trigger Verbosity Setting 
        """
        self.meta[ 'verbose' ] = True if self.meta[ 'verbose' ] is False else False
        return "[{}-{}]: Set Verbosity To {}.".format( self.meta[ 'purpose' ], self.meta[ 'id' ], self.meta[ 'verbose' ] )

    def _flushVerbosity( self, args, **kwargs ):
        """
            Flush Verbose state, called by XOBSRV
        """
        self.meta[ 'verbose' ] = False
        return "[{}-{}]: Flushed Observable State.".format( self.meta[ 'purpose' ], self.meta[ 'id' ] )
