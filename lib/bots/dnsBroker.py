#!/usr/bin/python

# Std lib
from re         import compile as reg_compile
from Queue      import Empty   as QueueEmpty
from random     import choice

# Custom libs
from bases      import LoggedBase
from dnsProbe   import Probe

class dnsBroker( LoggedBase ):

    def __init__( self, workerId, logPath, nameserver, qin = None, qout = None, metaQin = None, metaQout = None ):

        super( dnsBroker, self ).__init__( workerId      = workerId, 
                                           workerPurpose = "Probe",
                                           logPath       = logPath )

        self.state = {

            # Worker ID
            'id'      : workerId,

            # DNS Probe
            'probe'   : Probe( workerId = workerId, logPath = logPath, nameserver = nameserver ),

            # Google MX Regex
            'rgmx'    : reg_compile( "([0-9]+)\s(.*\.google(?:mail)?\.com$)" ),

            # SPF Regex
            'rgspf'   : reg_compile( '^"v\=(spf[0-9].*)"$' ),
            
            # Bot Run Status
            'alive'   : True,

            # I/O Queues
            'qin'     : qin,
            'qout'    : qout,

            # Meta Queues
            'mQin'    : metaQin,
            'mQout'   : metaQout,
        }

    def spam( self, node ):
        """
            Spam Respective Brokers With Metrics Harvested from
            Host objects for further perusal.

            @param Host host - Host() object containing host details to be logged
        """
        self.state[ 'qout' ].put( str( node ) )

    def build_host( self, node ):
        """
            Given the ip of a machine, perform a dns lookup for the following
            record types (in order): PTR, MX, TXT;

            @param String ip  - String representation of host ip
                                eg: "127.0.0.1"

            @return Host host - Host object containing returned dns records.
        """

        try:

            if node.url is not None:
                
                NodeId = node.url
                if self.state[ 'probe' ].resolve_a(   node ) is None: return node
                if self.state[ 'probe' ].resolve_mx(  node ) is None: return node
                self.state[    'probe' ].resolve_txt( node )

            elif node.a_records is not None:

                NodeId = node.a_records[0]
                if self.state[ 'probe' ].resolve_ptr( node ) is None: return node 
                if self.state[ 'probe' ].resolve_mx(  node ) is None: return node 
                self.state[    'probe' ].resolve_txt( node )

            else:
                self._log( 'build_host', 'DEBUG', 'Empty host object detected, unable to process {}'.format( node ) )

        except:
            self._log( 'build_host', 'DEBUG', 'Lookup has failed for {}'.format( NodeId ) )

        return node

    def background( self ):
        """
            Using queues have worker run unhindered, without the requirement
            of manually specifying individual host addresses. Designed to be
            used in tandem with multiprocessing.Process()

        """
        
        self._log( 'background', 'DEBUG', 'Starting Execution.' )
        while self.state[ 'alive' ]:

            # Process Meta Requests Before Starting On Current Host
            self._processMeta( self.state[ 'mQin' ], self.state[ 'mQout' ] )

            # Check For Queued Input
            try:
                HostData = self.state[ 'qin' ].get_nowait()

            except QueueEmpty:
                self._log( 'background', 'DEBUG', 'Nothing Queued For Processing [{}]'.format( self.state[ 'qin' ].qsize() )  )
                continue

            if type( HostData ) == str:
                if HostData.find( "STOP" ) != -1:
                    self._log( 'background', 'DEBUG', 'Recieved stop, inserting stop into output queue' )
                    self.state[ 'qout' ].put( 'STOP' )
                    self.state[ 'alive' ] = False
                    break
            
            # Buffer Last Processed Record 
            self.meta[ 'lrcd' ] = HostData

            # Retrieve Host Info
            host = self.build_host( HostData )

            # Spam Results To Brokers
            self.spam( host )

            # Increment Processed Record Count
            self.meta[ 'rcnt' ] += 1

        self._log( 'background', 'DEBUG', 'Execution completed' )
                
        return 
