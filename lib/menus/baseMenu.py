#!/usr/bin/python 

# Natives
from   datetime        import datetime
from   time            import sleep
from   collections     import namedtuple
import curses


import traceback


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

    def __init__( self, CommandAndControl = None, options = dict ):
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

        self.obj = { 
            'botMaster' : CommandAndControl,

            # Constants 
            'startTime' : datetime.now(),

            # Dynamic Information
            'screen'    : None,
            'subscr'    : None,
            'opt'       : Option, 

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
        

    def _sm_exit( self ):
        """
            Stop iteration 
        """
        raise StopIteration 

    def _poll( self ):
        """
              Abstract Method allows extending classes
            to interact with additional screens in the
            event that self._prepScreens() is overriden.
        """
        pass

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


    def _prepScreens( self, subscr ):
        """
                Prep framed screens returning output
            screen used between all menus.    

            @param curses.screen subscr

            @ret   curses.screen outputWindow
        """
        sy_max, sx_max = subscr.getmaxyx()
        return subscr.derwin( sy_max - 4, sx_max - 4, 3, 1 )

    def _menu( self ):
        """
            Generate Frame and Main Menu  
        """
        ( subscr, y_max, x_max ) = self._frame()

        sy_max, sx_max = subscr.getmaxyx()

        outputWin = self._prepScreens( subscr )
        oy_max, ox_max = outputWin.getmaxyx()
        outputWin.scrollok( 1 )

        # Save our subscreen to allow extending
        # classes to use it.
        self.obj[ 'subscr' ] = outputWin
        self.obj[ 'size'   ] = ( oy_max, ox_max ) 

        while True:
            selection = subscr.getch()

            for optName, option in self.menuOptions.iteritems():
                if selection in option.hotkeys:
                    self._poll()

                    #outputWin.addstr( oy_max - 1, 1, ': '.join( [ 'DEBUG', str(type( self.obj[ 'botMaster' ] )) ] ), curses.A_NORMAL )
                    outputWin.scroll()

                    # Do we require initialization?
                    if type( option.method ) == type:
                        optMenu = option.method( optName, self.obj[ 'botMaster' ] )
                        output  = ': '.join( optMenu.view()  )
                    else:
                        output  = ': '.join( option.method() ) 

                    outputWin.addstr( oy_max - 2, 1, output, curses.A_NORMAL )
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
        # Give ourselves a fresh template
        # Helps with submenus
        self.obj[ 'screen' ].clear()

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

if __name__ == '__main__':
    def cnc( *args, **kwargs ):
        """
            hehe
        """
        pass

    def update( subscr, y_max, x_max, nodeTemplate, optionTemplate ):
        return ( "UPDATE", "Propagated" )

    x = baseMenu( options = {
            'Update' : Option( 
                order   = 9,
                hotkeys = [ ord( 'u' ), ord( 'U' ) ],
                method  = update,
                display = [ ["U"], "pdate" ],
            ), 
        },
    )

    # CommandAndControl = cnc )
    x.view()
    del x
