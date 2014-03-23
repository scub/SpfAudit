#!/usr/bin/python

# External Dependencies
from   iptools  import IpRange 

# Internal Dependencies
from   baseMenu import Option
from   sm_Base  import sm_Base

# Py Natives
import curses

class sm_Input( sm_Base ):
    """

        Gotcha - As cidr notation is accepted, file input should only be
                 used for domains. ( But what about chunked infrastructure? )
    """
    def __init__( self, optName = str, CommandAndControl = None ):

        self.cnc = CommandAndControl

        super( sm_Input, self ).__init__( 
            options           = {
                'File'       : Option( 
                    order   = 0,
                    hotkeys = [ ord( 'f' ), ord( 'F' ) ],
                    method  = self.obtainInput, 
                    display = [ ["F"], "ile" ],
                ),

                'CIDR Block' : Option(
                    order   = 1, 
                    hotkeys = [ ord( 'c' ), ord( 'C' ) ],
                    method  = self.obtainInput, 
                    display = [ ["C"], "IDR Block" ],
                ),

                'Domain'     : Option(
                    order   = 2,
                    hotkeys = [ ord( 'd' ), ord( 'D' ) ],
                    method  = self.obtainInput, 
                    display = [ ["D"], "omain" ],
                       ),

                'Single IP'  : Option(
                    order   = 3,
                    hotkeys = [ ord( 'i' ), ord( 'I' ) ],
                    method  = self.obtainInput, 
                    display = [ "Single ", ["I"], "p" ],
                ),
            }
        )

        self.obj.update( { 'calls' : {
            'CIDR Block' : self.GenerateCIDR,
            'Single IP'  : self.GenerateIP, 
        } } )

    def GenerateCIDR( self, nodeTemplate ):
        """
            Given a cidr block, encapsulate in a node
            object and yield 
        """
        for nodePayload in IpRange( self.process ):
            yield nodeTemplate( a_records = [ nodePayload ] )

    def GenerateDom(  self, nodeTemplate ):
        pass
        
    # AS CIDR NOTATION IS ACCEPTED, FILES SHOULD 
    # ONLY BE USED TO FIRE THROUGH DOMAINS
    def GenerateFile( self, nodeTemplate ):
        pass

    def GenerateIP(   self, nodeTemplate ):
        for ip in [ self.process, ]:
            yield ip
    
    def obtainInput( self, option, cnc ):
        screen = curses.newwin( 3, 65, 4, 6 )
        screen.box()

        screen.addstr( 1, 2, " "*59, curses.A_UNDERLINE )
        screen.refresh()

        # Tell curses to allow feedback
        curses.echo()
        curses.nocbreak()

        # Obtain data and assign it for processing
        data_in = screen.getstr( 1, 2 )
        self.process = data_in

        for optIdentifier, call in self.obj[ 'calls' ].iteritems(): 
            if option == optIdentifier:
                self.cnc.evalGenerator( call )

        # Reset curses
        curses.noecho()
        curses.cbreak()

        return ( option, data_in )
