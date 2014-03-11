#!/usr/bin/python

from   Queue import Empty as QueueEmpty
from   time  import sleep
import curses

class sm_Base( object ):

    def __init__( self, screen, botMaster, botList, menuName, menuOptions = None, throttle = 1 ):
    
        super( sm_Base, self ).__init__()

        ( self.screen, 
          self.botMaster,
          self.botList,
          self.menuName,
          self.throttle   ) = ( screen,
                                botMaster,
                                botList,
                                menuName,
                                throttle ) 


        self.menuOptions = "(Q)uit" if menuOptions is None else "{} (Q)uit".format( menuOptions ) 

        self.SIGNALS = {
            # Stop observing, flushing queues
            'q' : ( "XOBSRV", None ),
        }

    def _frame( self, screen ):

        # Pull our terminal size to scale accordingly
        self.y_max, self.x_max = screen.getmaxyx()
        
        screen.clear()

        screen.border( 0 )
        screen.addstr( 1, 2, "Menu: {:<8}".format( self.menuName ), curses.A_NORMAL )
        screen.addstr( self.y_max - 1, 2, self.menuOptions, curses.A_NORMAL )

        screen.refresh()

        subScreen = screen.subwin( self.y_max - 4, self.x_max - 2, 3, 1 )
        subScreen.scrollok( 1 )

        # Non blocking getch
        subScreen.nodelay( 1 )

        return subScreen

    def _poll( self, screen ):

        key_in = screen.getch() 

        self.botMaster.pollWorkforce()
        # Can be more effecient PATCH.PATCH.PATCH 
        for key, signal in self.SIGNALS.iteritems():
            if key_in == ord( key ):
                if all( map( lambda x: x[ 'proc' ].is_alive(), self.botMaster.state[ self.botList ] ) ):
                    map( lambda broker: broker[ 'mQin' ].put( signal ), self.botMaster.state[ self.botList ] )
                else:
                    screen.addstr( self.y_max - 5, 2, "[!] {} has finished processing.".format( self.menuName ), curses.A_NORMAL )
                    screen.scroll() 

        return key_in

    def view( self ):

        screen  = self._frame( self.screen )
        Brokers = self.botMaster.state[ self.botList ]
        key_in  = screen.getch()

        # Have we been asked to exit?
        while all( map( lambda x: key_in != ord( x ), [ 'q', 'Q' ] ) ):

            for broker in Brokers:

                if not broker[ 'proc' ].is_alive(): continue

                try:
                    meta = broker[ 'mQout' ].get_nowait()
                    if "DATA" in meta[ 0 ]:
                        screen.addstr( self.y_max - 5, 2, "{}".format( meta[1] ), curses.A_NORMAL )
                        screen.scroll()
                except QueueEmpty as NoMetaToProcess:
                    pass

            sleep( 1 )

            key_in = self._poll( screen )
