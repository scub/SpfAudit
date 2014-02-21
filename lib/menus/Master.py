#!/usr/bin/python

# Stdlib
from   Queue    import Empty as QueueEmpty
from   datetime import datetime
from   time     import sleep
import curses

# SubMenus
from   sm_Probe import sm_Probe

class MainMenu( object ):

    def __init__( self, CommandAndControl = None, workerCount = None, logPath = None, targeting = None ): 

        self.meta = {

            # List of Name tuples containing our workers meta
            'startTime' : datetime.now(),

            'BotMaster' : CommandAndControl( workerCount = workerCount, logPath = logPath  ),

            # Curses 
            'screen'    : None,
            'subscr'    : None,
            'verbose'   : False, 
            'pos'       : 1,

            # SubMenus And Statuses
            'm_opts'    : {

                1 : ( 'dnsProbe',  sm_Probe       ),
                9 : ( 'Exit',      self._cleanup  ),

            }
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

        # Push Targets To Probes
        self.meta[ 'BotMaster' ].pushTargets( targeting )
        #raise NotImplemented

        self.meta[ 'BotMaster' ].powerWorkforce()

        # Setup default color-scheme and enable keypad input
        self.meta[ 'screen' ] = curses.initscr()
        curses.start_color()
        curses.noecho()
        #curses.nocbreak()
        self.meta[ 'screen' ].keypad( 1 )
        curses.init_pair( 1, curses.COLOR_YELLOW, curses.COLOR_BLACK )
        curses.init_pair( 2, curses.COLOR_GREEN,  curses.COLOR_GREEN )

        self.main()

    def _runtime2block( self ):

        runTime = datetime.now() - self.meta[ 'startTime' ]

        hours, minutes = "{:0>3}".format( runTime.seconds / 3600 ), "{:0>2}".format( ( runTime.seconds / 60 ) % 60 )

        output = []
        for ch in "{}:{}:{:0>2}".format( hours, minutes, runTime.seconds % 60 ):
            output.append( self.conversion[ ch ] )

        output_buf = zip( *output )
        del output[:] 

        for outputLine in output_buf:
            output.append( " ".join( outputLine ) )

        return output 

    def main( self ):

        menu_ret = self.master_menu()

        while True:
            
            option = menu_ret - 48

            if option in self.meta[ 'm_opts' ].keys():

                try:

                    self.meta[ 'm_opts' ][ option ][ 1 ]( self.meta[ 'screen' ], self.meta[ 'BotMaster' ] )

                except StopIteration as SignaledToExit: 
                    break

            menu_ret = self.master_menu( menu_name = self.meta[ 'm_opts' ][ option ][ 0 ] )


    def _cleanup( self, screen, BotMaster ):


        # TESTING ( Flush Output Queues Before Exiting )
        stopCount = 0
        cnc       = self.meta[ 'BotMaster' ]
        Qout      = cnc.state[ 'qout' ]

        while not Qout.empty() and stopCount != cnc.state[ 'workerCount' ]:
            try:
                HostData = Qout.get()
                if "STOP" not in HostData:
                    cnc._log( 'QueuedOutput', "DEBUG", HostData )
                else:
                    cnc._log( 'QueuedOutput', "DEBUG", "STOP Detected, Probe Shutdown Successful" )
                    stopCount += 1

            except QueueEmpty as FinishedProcessing:
                break
            except KeyboardInterrupt as HurryTheFudgeUp:
                break
        # /TESTING


        BotMaster.cleanupWorkforce()
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        screen.keypad( 0 )
        raise StopIteration


    def master_menu( self, menu_name = "Main" ):
        data_in = None 
        self.meta[ 'screen' ].nodelay( 1 )

        while data_in != ord( '\n' ):

            sleep( 1 )
            self.meta[ 'screen' ].clear()
            self.meta[ 'screen' ].border( 0 )

            self.meta[ 'screen' ].addstr( 1, 2, "Menu: {:<8}".format( menu_name ), curses.A_NORMAL )

            # Snag Our Positioning
            y_max, x_max = self.meta[ 'screen' ].getmaxyx()
            cur = ( y_max / 2 ) - 3 

            # Display Runtime
            self.meta[ 'screen' ].addstr( cur - 2, 5, "Run Time", curses.A_NORMAL )
            self.meta[ 'screen' ].addstr( cur - 1, 5, "========", curses.A_NORMAL )
            for line in self._runtime2block():
                self.meta[ 'screen' ].addstr( cur, 5, line, curses.A_NORMAL ) #( 2 ) ) 
                cur += 1

            # Menu Options
            for opt in sorted( self.meta[ 'm_opts' ], key = self.meta[ 'm_opts' ].get ): 

                # Are we hilighted? 
                if self.meta[ 'pos' ] != opt:
                    self.meta[ 'screen' ].addstr( opt + ( cur + 8 ), 4, "{} - {}".format( opt, self.meta[ 'm_opts' ][ opt ][ 0 ] ), curses.A_NORMAL )
                else:
                    self.meta[ 'screen' ].addstr( opt + ( cur + 8 ), 4, "{} - {}".format( opt, self.meta[ 'm_opts' ][ opt ][ 0 ] ), curses.color_pair( 1 ) )


            self.meta[ 'screen' ].refresh()
            data_in = self.meta[ 'screen' ].getch()

            if data_in == ord( '\n' ):
                break

            for opt in self.meta[ 'm_opts' ].keys():
                if data_in == ord( '{}'.format( opt ) ):
                    self.meta[ 'pos' ] = opt
                    break

            if data_in != ord( '\n' ):
                curses.flash()

        self.meta[ 'screen' ].keypad( 0 )
        return ord( str( self.meta[ 'pos' ] ) )
