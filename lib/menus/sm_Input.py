#!/usr/bin/python

# External Dependencies
from   iptools  import IpRange 

# Internal Dependencies
from   baseMenu import Option
from   sm_Base  import sm_Base

# Py Natives
from   lzma     import LZMAFile
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
                'Archive'    : Option(
                    order   = 0,
                    hotkeys = [ ord( 'a' ), ord( 'A' ) ],
                    method  = self.obtainInput,
                    display = [ ["A"], "rchive" ],
                ),

                'File'       : Option( 
                    order   = 1,
                    hotkeys = [ ord( 'f' ), ord( 'F' ) ],
                    method  = self.obtainInput, 
                    display = [ ["F"], "ile" ],
                ),


                'CIDR Block' : Option(
                    order   = 2, 
                    hotkeys = [ ord( 'c' ), ord( 'C' ) ],
                    method  = self.obtainInput, 
                    display = [ ["C"], "IDR Block" ],
                ),

                'Domain'     : Option(
                    order   = 3,
                    hotkeys = [ ord( 'd' ), ord( 'D' ) ],
                    method  = self.obtainInput, 
                    display = [ ["D"], "omain" ],
                       ),

                'Single IP'  : Option(
                    order   = 4,
                    hotkeys = [ ord( 'i' ), ord( 'I' ) ],
                    method  = self.obtainInput, 
                    display = [ "Single ", ["I"], "p" ],
                ),
            }
        )

        self.obj.update( { 'calls' : {
            'CIDR Block' : self.GenerateCIDR,
            'Single IP'  : self.GenerateIP, 
            'File'       : self.GenerateFile,
            'Archive'    : self.GenerateArchive,
            'Domain'     : self.GenerateDom,
        } } )

    def GenerateArchive( self, nodeTemplate ):
        """
            Given an xz compressed archive, read off its contents
            encapsulating each record in a node object for further
            processing upstream. 

            @param  Node nodeTemplate - Node object definition, used to encapsulte records
            @return None
        """
        fd = LZMAFile( self.process )

        # Yank Header Information
        buf = fd.next()

        # Begin processing
        while True:
            try:
                line = fd.next()
            except StopIteration as FinishedProcessing:
                break

            yield nodeTemplate( url = line.strip() ) 

        fd.close()

    def GenerateCIDR( self, nodeTemplate ):
        """
            Given a cidr block, encapsulate in a node
            object and yield 

            @param  Node nodeTemplate - Node object definition, used to encapsulte records
            @return None
        """
        for nodePayload in IpRange( self.process ):
            yield nodeTemplate( a_records = [ nodePayload ] )

    def GenerateDom(  self, nodeTemplate ):
        """
            Given a single domain, encapsulate it in a node
            object before yielding it for further processing.

            @param  Node nodeTemplate - Node object definition, used to encapsulte records
            @return None
        """
        for node in [ nodeTemplate( a_records = [ self.process ] ) ]:
            yield node

    # AS CIDR NOTATION IS ACCEPTED, FILES SHOULD 
    # ONLY BE USED TO FIRE THROUGH DOMAINS
    def GenerateFile( self, nodeTemplate ):
        """
            Given a flat file, read off its contents
            encapsulating each record in a node object 
            for further processing upstream.

            @param  Node nodeTemplate - Node object definition, used to encapsulte records
            @return None
        """
        with open( self.process, 'r' ) as fd:
            fd.readline()

            for line in fd.readlines():
                yield nodeTemplate( url = line.strip() )

    def GenerateIP( self, nodeTemplate ):
        """
            Given a single ip, encapsulate it in a node object
            using the nodeTemplate, then queue it for further 
            processing upstream.

            @param  Node nodeTemplate - Node object definition, used to encapsulte records
            @return None
        """
        for ip in [ self.process ]:
            yield ip
    
    def obtainInput( self, option, cnc ):
        """
            Create a new window to obtain user input.

            @param String            option   - Selected option
            @param CommandAndControl cnc      - Command And Control Object

            @return tuple ( 
                    STRING selectedOption,
                    STRING userInput,
            )
        """
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
                self.cnc.pushTargets( call )

        # Reset curses
        curses.noecho()
        curses.cbreak()

        return ( option, data_in )
