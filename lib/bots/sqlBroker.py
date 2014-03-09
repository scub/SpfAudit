#!/usr/bin/python
"""

    http://initd.org/psycopg/docs/advanced.html#async-support

    ''' when using a module such as multiprocessing -- create the connections after the fork. '''
    - the connection is always in autocommit mode 
    - With asynchronous connections it is also not possible to use set_client_encoding(), 
      executemany(), large objects, named cursors.

"""

from   Queue               import Empty as QueueEmpty
from   brokerBase          import brokerBase

# Postgresql Libs
from   psycopg2            import connect as Database
from   psycopg2.extensions import POLL_OK, POLL_READ, POLL_WRITE 

class sqlBroker( brokerBase ):

    def __init__( self, workerId, logPath, qin = None, metaQin = None, metaQout = None, geoip = None ):
        """
               Create a postgresql broker, prepping database structures for scanning
            and cataloging Host information.

            @param int        workerId   - Worker Id
            @param String     logPath    - Path to log to
            @param NameServer nameserver - Namerserver object
            @param Queue      qin        - Input Queue
            @param Queue      metaQin    - Meta Input Queue  (Used by menus)
            @param Queue      metaQout   - Meta Output Queue (Used by menus)
            @param Reader     geoip      - Initialized geoip2.database.Reader object
                                            ( Unrequired for this broker )

            @return sqlBroker
        """
        super( sqlBroker, self ).__init__( workerId      = workerId,
                                           workerPurpose = "SqlBroker",
                                           logPath       = logPath,
                                           qin           = qin,
                                           metaQin       = metaQin,
                                           metaQout      = metaQout, )

        # Stored Queries
        self.query = {

            # Create Table
            'ctable'   : """
                         CREATE TABLE IF NOT EXISTS MX (
                                id          SERIAL,
                                url         VARCHAR(150),
                                a_records   VARCHAR(250),
                                mx_records  VARCHAR(250),
                                txt_records VARCHAR(250),
                                spf_method  VARCHAR(10),
                                txt_present BOOLEAN ); """,

            # Catalog Given Node If Not Already In Database
            'insert'   : """
                         INSERT INTO MX ( url,
                                          a_records,
                                          mx_records,
                                          txt_records,
                                          spf_method,
                                          txt_present )
                         SELECT %(url)s,
                                %(ip)s,
                                %(mx)s,
                                %(txt)s,
                                %(spf)s,
                                %(txtp)s
                         WHERE NOT EXISTS (
                            SELECT *
                            FROM   MX
                            WHERE  url=%(url)s AND
                                   a_records LIKE %(constraint)s );
                         """,


        }

    def block( self, sqlConnection ):
        """
              Continually Poll A Given Sql Connection, blocking until a
              POLL_OK is recieved and the descriptor is ready for processing.

              @param psycopg2.connection  SqlConnection - Connection object to poll

              @return None
        """
        connectionState = sqlConnection.poll()
        while connectionState != POLL_OK:
            if connectionState > 3:
                print "Scotty we have a problem" 

            connectionState = sqlConnection.poll()


    def bootstrap( self ):
        """
              Initialize our database connection after our fork() has occured,
            this is due to the nature of the psycopg2 library when used with 
            psycopg2.connect( async = True )
           
            http://initd.org/psycopg/docs/usage.html#thread-and-process-safety

            @params None
            @return None
        """
        # Initialize database connection
        sqlCon = Database(  database = "SpfAudit", async = True )
            
        # Obtain our database descriptor once were ready to process
        self.block( sqlCon )
        sql = sqlCon.cursor()

        # Ensure schema intact before processing 
        sql.execute( self.query[ 'ctable' ] )
        self.block( sql.connection )

        # Propagate our master connection and cursor objects into
        # state structure. 
        self.state.update( {
            'sqlCon' : sqlCon,
            'sql'    : sql,
        } )

        
    def process( self, node ):
        """
              Given a Node object, execute a parameterized update-if-not-exists
            query against the database; only archiving if the given node has not
            been previously cataloged.

            @param lib.types.Node    Node object Containing Host details
        """
        if type( node ) != str:
            if all( map( lambda x: x is not None, 
                         [ node.url, node.a_records, node.mx_records ] ) ):

                ip = node.a_records if node.a_records is list else node.a_records[0]
                self.state[ 'sql' ].execute( self.query[ 'insert' ],
                    {
                        'url'        : node.url,
                        'ip'         : ip, 
                        'mx'         : node.mx_records,
                        'txt'        : node.txt_records,
                        'spf'        : node.spf_method,
                        'txtp'       : node.txt_present,
                        'constraint' : "%{}%".format( ip ),
                    } 
                )

        # Dont forget to clean up after ourselves 
        del node

        # Acquire descriptor access before transitioning
        # to next record
        try:
            self.block( self.state[ 'sql' ].connection )
        except Exception as e:
            self._log( 'process', 'CRITICAL', 'Trapped SQL Error: {}'.format( e ) )
            pass
