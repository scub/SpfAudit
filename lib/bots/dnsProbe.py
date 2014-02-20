#!/usr/bin/python

from dns.resolver import Resolver, NXDOMAIN, NoAnswer, Timeout
from bases import LoggedBase

class Probe( LoggedBase ):
    
    def __init__( self, workerId = None, logPath = None, nameserver = None ):

        # Initialize Logging Bases
        super( Probe, self ).__init__( workerId      = workerId,
                                       workerPurpose = 'dnsProbe',
                                       logPath       = logPath      )  
        
        self.state = {
            'id'         : workerId,
            'nameserver' : nameserver,
            'resolver'   : Resolver(),
        }


    def query( self, hostInfo, recordType ):
        """
            Query a random nameserver for the given host information,
            retrieving returned records, or returning None in the absence
            of them.
        """
        self.state[ 'resolver' ].nameservers = [ str( self.state[ 'nameserver' ] ) ]
        
        try:
            return self.state[ 'resolver' ].query( hostInfo, recordType )
        except NoAnswer as DNS_UNSET:
            self._log( 'query', 'INFO', 
                'No DNS Records Found - {}, {} => {}'.format( hostInfo, recordType, self.state[ 'resolver' ].nameservers[0] )
            )
            return None
        except ( NXDOMAIN, Timeout ) as FailedQuery:
            self._log( 'query', 'WARNING', 
                'Lookup Failed - {}, {} => {}'.format( self.state[ 'resolver' ].nameservers[0], recordType, hostInfo )
            )
            return None
        
    def resolve_ptr( self, node ):
        """
            Query a random nameserver for a given ip's rdns (PTR),
            and Strip out the base url returning the results. 

            eg:
                PTR = wow.this.is.a.really.long.rdns.url.tld

                return domain.tld
        """
        ptr = self.query( node.reverseName(), 'PTR' )
        node.url = None if ptr is None else ".".join( [ str( x ).lower() for x in ptr ][0].split( '.' )[-3:-1:1] )
        return node.url
            
    def resolve_mx( self, node ):
        """
            Query a random nameserver for a given host url's mail
            exchange (MX) records. Results are returned for
            inline processing.
        """
        mx = self.query( node.url, 'MX' )
        node.mx_records = None if mx is None else ",".join( [ str( x ).lower()[:-1] for x in mx ] )
        return node.mx_records
        
    def resolve_txt( self, node ):
        """
            Query a random nameserver for a given host url's txt
            records, in our case were specifically looking for spf 
            based records. Results are returned for inline processing.

        """
        txt = self.query( node.url, 'TXT' )
        node.txt_records = None if txt is None else ",".join( [ str( x ).lower() for x in txt ] )
        return node.txt_records

