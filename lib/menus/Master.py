#!/usr/bin/python

import curses, traceback
from   datetime import datetime
from   time     import sleep

# Externals
from   baseMenu import baseMenu, Option
from   sm_Input import sm_Input
from   sm_Bots  import sm_Bots

class Master( baseMenu ):

    def __init__( self, 
                  CommandAndControl = None, 
                  workerCount       = None,
                  eBrokerCount      = None,
                  sBrokerCount      = None,
                  logPath           = None,
                  geoipPath         = None,
                  targeting         = None ):

        
        cnc = CommandAndControl( 
            workerCount  = workerCount,
            eBrokerCount = eBrokerCount,
            sBrokerCount = sBrokerCount,
            logPath      = logPath,
            geoipPath    = geoipPath
        )

        super( Master, self ).__init__( 
            CommandAndControl = cnc,
            options           = {
                'Input'  : Option( 
                    order   = 0,
                    hotkeys = [ ord( 'i' ), ord( 'I' ) ],
                    method  = sm_Input,
                    display = [ ["I"], "nput" ],
                ),

                'Bots'   : Option(
                    order   = 1,
                    hotkeys = [ ord( 'b' ), ord( 'B' ) ],
                    method  = sm_Bots,
                    display = [ ["B"], "ots" ],
                ),

                # DEBUG
                'Poll'   : Option(
                    order   = 2,
                    hotkeys = [ ord( 'p' ), ord( 'P' ) ],
                    method  = self._pollCnC,
                    display = [ ["P"], "oll" ],
                ),

                'Pause/Play'  : Option(
                    order   = 3,
                    hotkeys = [ ord( 'a' ), ord( 'A' ) ],
                    method  = self._pauseCnC, 
                    display = [ "P", ["a"], "use/Pl", ["a"], "y" ],
                ),

                'Kill'   : Option(
                    order   = 4,
                    hotkeys = [ ord( 'k' ), ord( 'K' ) ],
                    method  = self._killCnC,
                    display = [ ["K"], "ill" ],
                ),

                'List'   : Option( 
                    order   = 5, 
                    hotkeys = [ ord( 'l' ), ord( 'L' ) ],
                    method  = self._listCnC, 
                    display = [ ["L"], "ist" ]
                ),
            }
        )

        # Time Conversions
        self.conversion = {
            '0' : [ "000000", "00  00", "00  00", "00  00", "000000" ],
            '1' : [ " 000  ", "0 00  ", "  00  ", "  00  ", "000000" ],
            '2' : [ "000000", "0  000", "  000 ", " 000  ", "000000" ],
            '3' : [ " 0000 ", "00  00", "   00 ", "0   00", " 0000 " ],
            '4' : [ "00  00", "00  00", "000000", "    00", "    00" ],
            '5' : [ "000000", "00    ", "000000", "    00", "00000 " ],
            '6' : [ " 00000", "00    ", "00000 ", "00   0", " 0000 " ],
            '7' : [ "000000", "00  00", "    00", "    00", "    00" ],
            '8' : [ "000000", "00  00", "000000", "00  00", "000000" ],
            '9' : [ "000000", "00  00", "000000", "    00", "000000" ],
            '/' : [ "    00", "   00 ", "  00  ", " 00   ", "00    " ],
            ' ' : [ "      ", "      ", "      ", "      ", "      " ],
            ':' : [ "  000  ", "  000  ", "       ", "  000  ", "  000  " ],
        }

        # Spin up our bots
        cnc.powerWorkforce()
        
        # Display the main menu
        self.view()

    def _killCnC( self ):
        cnc = self.obj[ 'botMaster' ]
        for i in range( cnc.state[ 'workerCount' ] ):
            cnc.state[ 'qin' ].put( "STOP" )

        # Allow workers to stop 
        # processing and flush queues
        sleep( 1 ) 
        cnc.pollWorkforce() 
        sleep( 1 ) 

        output = self._pollCnC( 'Kill Engaged' )
        cnc.stopWorkforce()
        return output

    def _listCnC( self ):
        cnc = self.obj[ 'botMaster' ]

        self._printScr( [ "Listing", "", "Bots", "====" ] )
        for botList in [ cnc.state[ i ] for i in [ 'workers',
                                                   'sqlBrokers',
                                                   'esBrokers' ] ]:
            self._printScr(
                [ "Bot: {}".format( bot[ 'proc' ].name ) for bot in botList ]
            )

        self._printScr( [ "", "Conf", "====" ] )
        for name, check in [ ( i, cnc.state[ i ] ) for i in [ 'lastId',
                                                              'throttle',
                                                              'target_count',
                                                              'botsPaused',
                                                              'exitQueued' ] ]: 
            self._printScr( "Conf: {} => {}".format( name, str( check ) ) )

        return ( 'Listing', 'Finished' )

    def _pauseCnC( self ):
        ret = self.obj[ 'botMaster' ].pauseWorkforce()

        self.obj[ 'screen' ].refresh()
        self.obj[ 'subscr' ].refresh()

        curses.noecho()
        curses.cbreak()
        return self._pollCnC( ret )

    def _pollCnC( self, pollInitiator = "Poll" ):
        cnc, results = self.obj[ 'botMaster' ], list()

        # Target Count
        results.append( 'Targets [ {} ];'.format( cnc.state[ 'target_count' ] ) )

        # Worker State 
        for name, workerList in [ ( i, cnc.state[ i ] ) for i in [ 'esBrokers', 
                                                                   'sqlBrokers', 
                                                                   'workers'     ] ]:

            if len( workerList ) > 0 and all(
                map( lambda bot: bot[ 'proc' ].is_alive(), workerList ) ):
                workerState = "Alive"
            else:
                workerState = "Dead"

            results.append( '{} -> [{}];'.format( name, workerState ) )

        results.append( self._getTime() )
        return ( pollInitiator, ' '.join( results ) )

    def _runtime2block( self, screen ):
        """
             Given a screen object, convert our runtime to block letters,
            and display it on the screen.

            @param curses.screen screen
        """
        runTime = datetime.now() - self.obj[ 'startTime' ]

        hours, minutes = "{:0>3}".format( runTime.seconds / 3600 ), "{:0>2}".format( ( runTime.seconds / 60 ) % 60 )

        output, displacement = [], 1
        for ch in "{}:{}:{:0>2}".format( hours, minutes, runTime.seconds % 60 ):
            output.append( self.conversion[ ch ] )

        for line in zip( *output ):
            screen.addstr( displacement, 1, " ".join( line ), curses.A_NORMAL )
            displacement += 1

        screen.refresh()

    def _prepScreens( self, subscr ):
        sy_max, sx_max = subscr.getmaxyx()

        self.timeWin = subscr.derwin(           8, sx_max - 9,  3, 5 )
        return         subscr.derwin( sy_max - 12, sx_max - 4, 11, 1 ) 

    def _poll( self ):
        """
            Return None To An Unneeded Scroll 
        """
        self._runtime2block( self.timeWin )
        return None 
