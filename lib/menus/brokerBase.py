#!/usr/bin/python

import curses, traceback
from   datetime import datetime
from   time     import sleep

from   baseMenu import baseMenu, Option

class brokerBase( baseMenu ):

    def __init__( self, CommandAndControl = None, botList = None, menuName = 'Base' ):
        """
        @param CommandAndControl CommandAndControl - We pass a reference to the
                                                     initialized command and control
                                                     object, to obtain access to worker
                                                     queues.

        @param String            botList           - Here we pass a string referencing
                                                     which brokers we are going to be 
                                                     acting on when the menu initializes.

        @param String            menuName          - We give the menu an identifying name
                                                     through the use of this variable.
        """
        super( brokerBase, self ).__init__(
            CommandAndControl = CommandAndControl,
            menuName          = menuName,
            options           = {
                # Dummy Option To Give Menu Fancy Name
                'Menu Name'   : Option(
                    order   = 0,
                    hotkeys = list(),
                    method  = self._pass(),
                    display = [ "{}:".format( menuName ) ],
                ),
                'Verbose'     : Option(
                    order   = 1,
                    hotkeys = [ ord( 'v' ), ord( 'V' ) ],
                    method  = self._signalVerbose, 
                    display = [ ["V"], "erbose" ],
                ),
                'Last Record' : Option(
                    order   = 2,
                    hotkeys = [ ord( 'l' ), ord( 'L' ) ],
                    method  = self._signalLast,
                    display = [ ["L"], "ast Record" ],
                ),
                'Status'      : Option(
                    order   = 3,
                    hotkeys = [ ord( 's' ), ord( 'S' ) ],
                    method  = self._signalStatus,
                    display = [ ["S"], "tatus" ],
                ),
                'Exit'        : Option(
                    order   = 10,
                    hotkeys = [ ord( 'x' ), ord( 'X' ) ],
                    method  = self._signalExit,
                    display = [ "E", ["x"], "it" ],
                ), 
            }
        )

        self.botList = botList

    def _pass( self ):
        """
            Null Function, Used as buffer for menu name
        """
        pass

    def _getTime( self ):
        """
            Returns the current time in our standard time format
            @return STRING 
        """
        return datetime.today().strftime( "%a %b %y, %H:%M:%S" )

    def _signalBots( self, option = None, signal = None, data = None ):
        """
            @param STRING signal - Signal to propagate through to bots
            @param STRING data   - Any extra data to be passed through
                                   with the signal.
        """
        # Do we have a signal, access to cnc, and a worker list?
        if all( map( lambda x: x is not None, 
                     [ option, signal, self.obj[ 'botMaster' ], self.botList ] ) ):

            # Snag the list of bots
            brokers = self.obj[ 'botMaster' ].state[ self.botList ] 

            try:
                # Spam Signal across all queues
                map( lambda broker: broker[ 'mQin' ].put( ( signal, data ) ), brokers )
                return ( option, "Queued {}.".format( self._getTime() ) ) 
            except:
                pass
        return ( option, "Required objects are not present, unable to process request." )

    def _signalExit( self ):
        """
              Signal All Workers To Turn Off Verbosity
            Flushing meta queues before cleanly exiting
            the submenu.
        """ 
        return self._signalBots( option = "EXIT", signal = "XOBSRV", data = None )

    def _signalLast( self ):
        """
               Signal all workers to display their last
            processed record.

        """ 
        return self._signalBots( option = "LAST", signal = "LPROC", data = None )

    def _signalStatus( self ):
        """
               Signal all workers to display their current
            status, including processed record counts and
            the last processed record.

        """    
        return self._signalBots( option = "STATUS", signal = "ALL", data = None )

    def _signalVerbose( self ):
        """
              Signal All workers to turn on verbosity
            records are displayed as they are processed.

        """
        return self._signalBots( option = "VERBOSE", signal = "VERBOSE", data = None )
