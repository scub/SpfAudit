#!/usr/bin/python 

# Natives
from   datetime        import datetime
from   time            import sleep
from   collections     import namedtuple
import curses, traceback


Option = namedtuple( "Option", "order hotkeys method display" ) 
class baseMenu( object ):
    """
          Master Menu provides access to all sub menus, provides
        overall run time information and the ability to feed targets 
        through the mechanism.
        
        Private
        -------

        Public
        ------
        view() 

    """

    def __init__( self, options = dict, showTime = False ):
        """

            @param CommandAndControl CommandAndControl
            @param INT               workerCount
            @param INT               eBrokerCount
            @param INT               sBrokerCount
            @param STRING            logPath
            @param STRING            geoipPath
            @param GENERATOR         targeting   
        """
        super( baseMenu, self ).__init__()


        self.obj= { 

            # Constants 
            'startTime' : datetime.now(),

            # Dynamic Information
            'screen'    : None,
            'showTime'  : showTime,
            'opt'       : Option, 

        }

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

        self.menuOptions = {
            'Exit'   : Option(
                         order   = 10,
                         hotkeys = [ ord( 'x' ), ord( 'X' ) ],
                         method  = self._sm_exit,
                         display = [ "E", ["x"], "it" ],
                       ),
        }

        self.menuOptions.update( options ) 

        self.obj[ 'screen' ] = curses.initscr()
        self.obj[ 'screen' ].keypad( 1 )
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        
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

    def _sm_exit( self, subscr, y_max, x_max, nodeTemplate ):
        """
            Stop iteration 
        """
        raise StopIteration 

    def _flushQueue( self, queue ):
        """
             Flush the contents of a given queue, incrementing
            the stop counter to act as a sanity check.

            @param Queue queue - Queue to be flushed
        """
        stopCount = 0
        cnc       = self.obj[ 'BotMaster' ]
        Qout      = cnc.state[ queue ]

        while not Qout.empty() and stopCount != cnc.state[ 'workerCount' ]:
            try:
                HostData = Qout.get()
                if type( HostData ) != str:
                    cnc._log( 'QueuedOutput', "DEBUG", HostData )
                else:
                    cnc._log( 'QueuedOutput', "DEBUG", "STOP Detected, Probe Shutdown Successful" )
                    stopCount += 1

            except QueueEmpty as FinishedProcessing:
                break
            except KeyboardInterrupt as UncleanExit:
                break
                
    def __del__( self ):
        """
               Return terminal to normal operation,
            undoing all changes required for curses
        """
        self.obj[ 'screen' ].clear()
        self.obj[ 'screen' ].keypad( 0 )
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def _menu( self ):
        """
            Generate Frame and Main Menu  
        """
        ( subscr, y_max, x_max ) = self._frame()

        sy_max, sx_max = subscr.getmaxyx()

        # Sub Windows
        if self.obj[ 'showTime' ]:
            timeWin         = subscr.derwin( 8,           sx_max - 9,  3, 5 )
            outputWin       = subscr.derwin( sy_max - 12, sx_max - 4, 11, 1 ) 
        else:
            outputWin       = subscr.derwin( sy_max - 4,  sx_max - 4,  3, 1 )

        oy_max, ox_max = outputWin.getmaxyx()

        outputWin.scrollok( 1 )

        while True:
            selection = subscr.getch()

            for optName, option in self.menuOptions.iteritems():
                if selection in option.hotkeys:
                    # Show runtime if requested
                    if self.obj[ 'showTime' ]: self._runtime2block( timeWin )

                    output = option.method( subscr, y_max, x_max, None )

                    outputWin.addstr( oy_max - 1, 1, ':'.join( output ), curses.A_NORMAL )
                    outputWin.scroll()
                    outputWin.refresh()
                    subscr.refresh()
                    
    def _frame( self ):
        """
            Setup frame for all menus

            @return tuple ( 
                @return subwin   screen - 'Framed' curses subwin() object,
                @return int      y_max  - Maximum terminal height,
                @return int      x_max  - Max terminal width )
        """
        y_max, x_max = self.obj[ 'screen' ].getmaxyx()
        screen       = self.obj[ 'screen' ].subwin( y_max - 1, x_max - 1, 0, 0 )
        y_max, x_max = screen.getmaxyx() 

        # Frame Window 
        screen.box()
        screen.hline(  2, 1, curses.ACS_HLINE, x_max - 3 )

        # Iterate given menu options building our menu list
        charCount, optList = 2, []
        for key, opt in self.menuOptions.iteritems():
           optList.append( ( key, opt.order ) ) 

        for option, optOrder in sorted( optList, key = lambda tup: tup[1] ):

            for section in self.menuOptions[ option ].display:
                if type( section ) == str:
                    screen.addstr( 1, charCount, "{}".format( section ),      curses.A_NORMAL    )
                    charCount += len( section )
                else:
                    screen.addstr( 1, charCount, "{}".format( section[ 0 ] ), curses.A_UNDERLINE )
                    charCount += 1

            charCount += 1

        del optList
        # Make our changes visible
        screen.refresh()

        return ( screen, y_max, x_max )


    def view( self ):
        """
            Display main menu
        """
        try:
            self._menu()
        except StopIteration as ExitCalled:
            self.__del__()
            return
