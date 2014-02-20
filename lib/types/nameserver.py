#!/usr/bin/python

from random import choice

class NameServer( object ) :
    
    def __init__( self ): 
        self.nameservers = {                          
                            
            # AWS INTERNAL - Fail 
            #'72.16.0.23'     : 0,
            
            # Google DNS
            '8.8.8.8'        : 0,
            '8.8.4.4'        : 0,
             
            # DNS Advantage
            '156.154.70.1'   : 0,
            '156.154.71.1'   : 0,
            
            # Norton Connect Safe
            '198.153.192.1'  : 0,
            '198.153.194.1'  : 0,
            
            # Comono
            '8.26.56.26'     : 0,
            '8.20.247.20'    : 0,
            
            # Safe DNS
            '195.46.39.39'   : 0,
            '195.46.39.40'   : 0,
            
            # OpenDNS
            '208.67.222.222' : 0,
            '208.67.220.220' : 0,
            
            # DynDNS
            '216.146.35.35'  : 0,
            '216.146.36.36'  : 0,
            
            # Hurricane Electric
            '74.82.42.42'    : 0,
            
            # Green Team DNS (sucks)
            #'81.218.119.11'  : 0
        }
    
    def stats( self ):
        for key, val in self.nameservers.iteritems():
            print "[",key,"] =>",val
    
    def __str__( self ):
        nameserver = choice( [ key for key in self.nameservers.iterkeys() ] )
        self.nameservers[ nameserver ] += 1
        return nameserver


if __name__ == '__main__':
        from random import choice
        
        x = NameServer()
        # Query random nameserver i time
        for i in range( choice( range( 25 ) ) ):
               print str( x )

        print x.stats() 
