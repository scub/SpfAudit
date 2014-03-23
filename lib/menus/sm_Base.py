#!/usr/bin/python

from   baseMenu import Option
import curses

import traceback

class sm_Base( object ):

    def __init__( self, y_src = 2, x_src = 1, lines = 7, cols = 17, options = dict, cnc = None ):
        """
            @param int    y_src    - Y Axis to start at
            @param int    x_src    - X Axis to start at
            @param int    lines    - Number of lines
            @param int    cols     - Number of columns
            @param dict() options  - Options list
        """

        super( sm_Base, self ).__init__()

        self.inputOptions = dict()

        self.obj = {
            'subMenu' : curses.newwin( lines, cols, y_src, x_src ),
            'cnc'     : cnc,
        }

        self.inputOptions.update( options )
        
    def _prepOptions( self ):
        """
            Setup menu with elements in options list
        """
        optList, lineCount = list(), 1

        for key, opt in self.inputOptions.iteritems():
            optList.append( ( key, opt.order ) ) 

        # For every menu option, sorted by order
        for option, optOrder in sorted( optList, key = lambda tup: tup[ 1 ] ):

            # Write it to the screen
            charCount = 2
            for section in self.inputOptions[ option ].display:
                if type( section ) == str:
                    self.obj[ 'subMenu' ].addstr( lineCount, charCount,      section, curses.A_NORMAL    )
                    charCount += len( section )
                else:

                    self.obj[ 'subMenu' ].addstr( lineCount, charCount, section[ 0 ], curses.A_UNDERLINE )
                    charCount += len( section[ 0 ] )
        
            lineCount += 1

        self.obj[ 'subMenu' ].box()
        self.obj[ 'subMenu' ].refresh()

    def view( self ):
        """
        """
        self._prepOptions()
        selection = ""

        while selection not in [ ord( 'x' ), ord( 'X' ) ]:
            selection = self.obj[ 'subMenu' ].getch()

            for optName, option in self.inputOptions.iteritems():
                if selection in option.hotkeys:

                    #<DEBUG>
                    with open( 'rawr.log', 'wa+' ) as fd:

                        fd.write( '\t[!] sm_Base.Function -> {}\n'.format( option.method.__name__ ) )
                        fd.write( '\t\t- Type: {}\r\n'.format( str( type( option.method ) ) ) ) 
                        for line in traceback.extract_stack()[:-1]:
                            fd.write( "\t\t{}\r\n".format( ': '.join( [ str(x) for x in line ] ) ) )
                    #</DEBUG>

                    optMenu = option.method( optName, self.obj[ 'cnc' ] )

                    if type( optMenu ) == tuple: return optMenu
                    return optMenu.view()

        return ( "Sub-Menu", "Closed" )
