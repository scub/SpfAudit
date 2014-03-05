#!/usr/bin/python

# Std lib
from re         import compile as reg_compile
from Queue      import Empty   as QueueEmpty
from random     import choice

# Custom libs
#from bases      import LoggedBase
from brokerBase import brokerBase
from dnsProbe   import Probe

class dnsBroker( brokerBase ):

    def __init__( self, 
                  workerId, 
                  logPath, 
                  nameserver, 
                  qin       = None, 
                  sqout     = None, 
                  eqout     = None,
                  metaQin   = None, 
                  metaQout  = None, 
                  geoip     = None ):
        """

               Create DNS Broker, Solicit's Nameservers for Queued host
            information before forwarding host object to aggregation 
            brokers. 
            
            @param int        workerId   - Worker Id
            @param String     logPath    - Path to log to
            @param NameServer nameserver - Namerserver object
            @param Queue      qin        - Input Queue
            @param Queue      sqout      - SqlBroker Input  Queue
            @param Queue      eqout      - Json Broker Output Queue
            @param Queue      metaQin    - Meta Input Queue  (Used by menus)
            @param Queue      metaQout   - Meta Output Queue (Used by menus)
            @param Reader     geoip      - Initialized geoip2.database.Reader object

        """

        super( dnsBroker, self ).__init__( workerId      = workerId, 
                                           workerPurpose = "Probe",
                                           logPath       = logPath,
                                           qin           = qin, 
                                           metaQin       = metaQin,
                                           metaQout      = metaQout )

        self.state.update( {

            # DNS Probe
            'probe'   : Probe( workerId   = workerId, 
                               logPath    = logPath, 
                               nameserver = nameserver ),

            # Google MX Regex
            'rgmx'    : reg_compile( "([0-9]+)\s(.*\.google(?:mail)?\.com$)" ),

            # SPF Regex
            'rgspf'   : reg_compile( '^"v\=(spf[0-9].*)"$' ),
            
            # Output QUeues
            'sqout'   : sqout,
            'eqout'   : eqout,


            # GeoIp Db Wrapper
            'geoip'   : geoip,
 
        } )

    def spam( self, node ):
        """
            Spam Respective Brokers With Metrics Harvested from
            Host objects for further perusal.

            @param  Host host - Host() object containing host details to be logged

            @return None
        """
        map( lambda queue: queue.put( node ), 
             [ self.state[ i ] for i in [ 'eqout', 'sqout' ] ] )

    def build_host( self, node ):
        """
            Given the ip or url of a machine, perform a dns lookup for 
            the following record types (in order): (PTR|A), MX, TXT;

            @param  Node node - Node() object prepped with a_records or url

            @return Host host - Host object containing returned dns records.
        """

        try:

            if node.url is not None:
                
                NodeId = node.url
                if self.state[ 'probe' ].resolve_a(   node ) is None: return node

            elif node.a_records is not None:

                NodeId = node.a_records[0]
                if self.state[ 'probe' ].resolve_ptr( node ) is None: return node 

            else:
                self._log( 'build_host', 'DEBUG', 'Empty host object detected, unable to process {}'.format( node ) )

            # Pull Coords If Geoip Available
            if self.state[ 'geoip' ] is not None:
                self.state[ 'probe' ].pull_geoip( node, self.state[ 'geoip' ] )

            # Ignore everything without an exchange
            if self.state[ 'probe' ].resolve_mx(  node ) is None: return None 

            # Pull down our TXT records
            if self.state[ 'probe' ].resolve_txt( node ) is None: return node

        except:
            self._log( 'build_host', 'DEBUG', 'Lookup has failed for {}'.format( NodeId ) )

        return node


    def process( self, node ):

        host = self.build_host( node ) 
        del node
        if host is not None:
            self.spam( host )
