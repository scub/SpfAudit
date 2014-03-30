#!/usr/bin/python

from Queue                    import Empty as QueueEmpty
from elasticsearch            import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from bases                    import LoggedBase
from brokerBase               import brokerBase

class esBroker( brokerBase ):

    def __init__( self, workerId, logPath, qin = None, metaQin = None, metaQout = None, geoip = None ):

        super( esBroker, self ).__init__( workerId      = workerId,
                                          workerPurpose = "ElasticBroker",
                                          logPath       = logPath,
                                          qin           = qin,
                                          metaQin       = metaQin,
                                          metaQout      = metaQout )

        self.state.update( {
            'es'    : Elasticsearch(), 
            'geoip' : geoip,
            'alive' : True,
        } )


    def find( self, node ):
        """

        """
        try:
            res = self.state[ 'es' ].search( index = 'spfaudit', body = {
                'query' : { 'term' : { 
                    'url' : node.url,
                    'ip'  : node.a_records if type( node.a_records ) != list else node.a_records[0],
                } }
            } ) 

            return False if res[ 'hits' ][ 'total' ] == 0 else True 

        except NotFoundError as Uncataloged:
            return False

    def process( self, node ):
        """
            
        """
        # do we have a node object?
        if type( node ) == str: return

        # Do we fit the aggregation requirements?
        if not all( map( lambda x: x is not None,
                         [ node.url, node.a_records, node.mx_records ] ) ): return

        # Have we already been cataloged?
        if self.find( node ): return         

        # Woohoo, A New Boxen. Lets Catalog It!
        self.state[ 'es' ].index( 
            index    = "spfaudit", 
            doc_type = "node", 
            body     = node.convert( 
                'json', 
                self.state[ 'geoip' ] 
            )
        )
