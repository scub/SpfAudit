#!/usr/bin/python

from   Queue  import Empty as QueueEmpty
from   time   import sleep
import curses

def sm_Probe( screen, BotMaster ):

    SIGNALS = {
        'w' : ( "VERBOSE", None ),
        'p' : ( "LPROC",   None ),
        's' : ( "ALL",     None ),
        'q' : ( "XOBSRV",  None ),
    }

    screen.clear()

    key_in = None

    y_max, x_max = screen.getmaxyx()

    screen.border( 0 )
    screen.addstr( 1, 2, "Menu: {:<8}".format( "DNS Probe" ), curses.A_NORMAL ) 
    screen.addstr( y_max - 1, 2, "(W)atch (S)tatus (P)rogress (Q)uit", curses.A_NORMAL )

    screen.refresh()

    subscr = screen.subwin( y_max - 4, x_max - 2, 3, 1 )
    subscr.scrollok( 1 )

    # Non Blocking getch
    subscr.nodelay( 1 )

    Workers = BotMaster.state[ 'workers' ]
    while all( map( lambda x: key_in != ord( x ), [ 'q', 'Q' ] ) ):

        for worker in Workers:

            try:
                meta = worker[ 'mQout' ].get_nowait()
                if "DATA" in meta[0]:
                    subscr.addstr( y_max - 5, 2, "{}".format( meta[ 1 ] ), curses.A_NORMAL )
                    subscr.scroll()
            except QueueEmpty as NoMetaToProcess:
                pass


            ''' No Need To Send Our Hard Workers Results into the abyss
            try:
                if not worker.obj.is_alive(): continue
                output = worker.qout.get_nowait()
            except QueueEmpty as AwaitingInput:
                pass
            '''

        sleep( 1 )

        # Check for keys
        key_in = subscr.getch()
        for key, signal in SIGNALS.iteritems():
            if key_in == ord( key ):
                if all( map( lambda x: x[ 'proc' ].is_alive(), Workers ) ):
                    map( lambda x: x[ 'mQin' ].put( signal ), Workers )
                else:
                    subscr.addstr( y_max - 5, 2, "[!] DNS Probe Has Finished Enumerating", curses.A_NORMAL ) 
                    subscr.scroll()
