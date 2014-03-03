#!/usr/bin/python

from Queue                    import Empty as QueueEmpty
from elasticsearch            import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from bases                    import LoggedBase
from geoip2.database          import Reader
from datetime                 import datetime

class esBroker( LoggedBase ):

    def __init__( self, workerId, logPath, qin = None, metaQin = None, metaQout = None, geoip = None ):

        super( esBroker, self ).__init__( workerId      = workerId,
                                          workerPurpose = "ElasticBroker",
                                          logPath       = logPath )

        self.state = {

            'id'    : workerId,
            'es'    : Elasticsearch(), 
            'qin'   : qin,
            'mQin'  : metaQin,
            'mQout' : metaQout,
            'geoip' : geoip,
            'alive' : True,

        }

    def process( self, node ):
        """
            
        """
        if type( node ) != str:
            if all( map( lambda x: x is not None,
                         [ node.url, node.a_records, node.mx_records ] ) ):

                obj = node.convert( 'json', self.state[ 'geoip' ] )

                try: 
                    res = self.state[ 'es' ].search( index = "spfaudit", body = { "query": {
                        "term": {
                            'url'  : node.url,
                            'ip'   : node.a_records[0],
                        }   
                    }})

                    if res[ 'hits' ][ 'total' ] == 0:
                        self.state[ 'es' ].index( index     = "spfaudit", doc_type  = "node", body = obj )
                except NotFoundError as IndexNonExistant:
                    self.state[ 'es' ].index( index     = "spfaudit", doc_type  = "node", body = obj )

    def background( self ):
        """

        """
        while self.state[ 'alive' ]:

            self._processMeta( self.state[ 'mQin' ], self.state[ 'mQout' ] )
        
            try:
                NodeObj = self.state[ 'qin' ].get_nowait()

            except QueueEmpty as AwaitingNodeObject:
                continue

            if type( NodeObj ) != str:

                # Buffer last record
                self.meta[ 'lrcd' ] = NodeObj

                # Process Node Object
                self.process( NodeObj )

                # Increment Record Counter
                self.meta[ 'rcnt' ] += 1

            else:
                self._log( 'background', 'DEBUG', 'Recieved stop, stopping execution' )
                self.state[ 'alive' ] = False
                break

        self._log( 'background', 'DEBUG', 'Execution Complete' )

        return 
