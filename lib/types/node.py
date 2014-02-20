#!/usr/bin/python

from re       import match as regMatch
from random   import choice
from datetime import datetime

class Node( object ):
    """
        Node( Object )

            This object is used to aggregate collected records and statistics for a given node.

        Records
        =======

            a_records            - List Of Domain A Records

            mx_records           - List Of Domain MX Records

            txt_records          - List Of Domain Txt Records 

        Statistics
        ==========

            mx_hosted          - Internal (MX In Same Domain As Url)
                                 External (MX Hosted By Third Parties, Not Including Google)
                                 Google   (MX Hosted By Google)

            txt_present        - Boolean  (Are Txt Records Available For This Domain?)

            spf_method         - None     (No spf blocking)
                                 AllowAll (Allow all mail through *Bad Practice*)
                                 Neutral  ('Nothing Can Be Said About Validity' *Bad Practice*)
                                 SoftFail (Marked As Not Allowed But Still Allowed Passage *Bad Practice*
                                 HardFail (Marked As Not Allowed And Stopped At The Exchange !Best Practice!)

            preferred_exchange - Preferred Mail Exchange For Domain

    """
    def __init__( self, 
                  url                = None,
                  a_records          = None,
                  mx_records         = None,
                  txt_records        = None, 
                  txt_present        = None,
                  mx_hosted          = None,
                  spf_method         = None,
                  preferred_exchange = None ):
        """
            Create New Node Object
            

            @param String url                - URL Of Domain
            @param List   a_records          - List Of Domain A Records
            @param List   mx_records         - List Of Domain MX Records
            @param List   txt_records        - List Of Domain Txt Records 

            @param String mx_hosted          - Internal (MX In Same Domain As Url)
                                               External (MX Hosted By Third Parties, Not Including Google)
                                               Google   (MX Hosted By Google)
                                               None     (No Valid MX Found, Ignore)

            @param String spf_method         - None     (No spf blocking)
                                               AllowAll (Allow all mail through *Bad Practice*)
                                               Neutral  ('Nothing Can Be Said About Validity' *Bad Practice*)
                                               SoftFail (Marked As Not Allowed But Still Allowed Passage *Bad Practice*
                                               HardFail (Marked As Not Allowed And Stopped At The Exchange !Best Practice!)

            @param String preferred_exchange - Preferred Mail Exchange For Domain.
        """
        ( self.url,
          self.a_records,
          self.mx_records,
          self.txt_records,
          self.mx_hosted,
          self.txt_present,
          self.spf_method,
          self.preferred_exchange ) = ( url, 
                                        a_records,
                                        mx_records,
                                        txt_records,
                                        mx_hosted,
                                        txt_present,
                                        spf_method,
                                        preferred_exchange )

        
        
    def __str__( self ):
        """
            Possibly return a tuple for later insertion into the sql statement
            using the injection filtering ? functionality.
        """
        Output = [ "Node( {} ):".format( self.url ), ] 
        for key, value in self.convert( 'json' ).iteritems():
            Output.append( "\t{:<20} = {}".format( key, value ) ) 

        Output.append( '\n' )

        return '\n'.join( Output )

    
    def convert( self, requested_form = "sql" ):
        """
                Convert node object into desired form, Options include
            sql and json.

            @param String requested_form - Desired form of output available options
                                           'sql', 'json' 
            
            @return Tuple()   - Tuple Containing SQL Statement And Required Information ('sql' )
                    Dict()    - Dictionary Containing Meta Statistics For Given Node    ('json') 
        """

        available_repr = {
            # Collected Data ( Postgresql - SQL Broker )
            'sql'  : ( "INSERT INTO ? VALUES ( ?, ?, ?, ?, ?, ?, ? );",
                         (
                            'NULL' if self.url           is None else "'{}'".format( self.url         ),
                            'NULL' if self.a_records     is None else "'{}'".format( self.a_records   ),
                            'NULL' if self.mx_records    is None else "'{}'".format( self.mx_records  ),
                            'NULL' if self.txt_records   is None else "'{}'".format( self.txt_records ),
                            'NULL' if self.mx_hosted     is None else "'{}'".format( self.mx_hosted   ),
                            'NULL' if self.spf_method    is None else "'{}'".format( self.spf_method  ),
                            1      if self.txt_present   is True else 0 
                         ) 
                     ),


            # Meta Statistics ( Elastic Search - JSON Broker )
            'json' : {
                        # Elastic Search Event Type
                        'type'               : 'Node',

                        # Collection Timestamp
                        'timestamp'          : datetime.ctime( datetime.now() ),

                        # Txt Records Present
                        'txt_present'        : True if self.txt_records is not None else False,

                        # Hosted By: Internal (Matches URL), Google Mail
                        'mx_hosted'          : self._checkMxHosted(),

                        # Preferred Exchange
                        'preferred_exchange' : self._preferredExchange(), 

                        # None, Soft, Hard
                        'spf_method'         : self._checkSpfMethod(),

                     },
        }

        return None if not available_repr.has_key( requested_form ) else available_repr[ requested_form ] 

    def _preferredExchange( self ):
        """
            Return preferred exchange for domain

            @return String - Perferred Exchange
        """
        records = []
        try:
            for dnsRecord in self.mx_records.split( ',' ):
                preference, exchange = dnsRecord.split(' ')

                records.append( ( preference, exchange ) )
        except AttributeError:
            return None

        return sorted( records, key = lambda tup: tup[1] )[0][1]
        

    def _checkMxHosted( self ):
        """
            Check Where Mail Exchanges Are Hosted

            @return String - Internal (MX In Same Domain As Url)
                             External (MX Hosted By Third Parties, Not Including Google)
                             Google   (MX Hosted By Google)
        """

        # Do We Have Valid Records To Check?
        if self.mx_records is None: return None                

        # Yank the exchanges from our mx records
        exchanges = map( lambda record: record.split()[1], self.mx_records.split( ',' ) )

        # Does Google Host? 
        if all( map( lambda x: True if regMatch( "^(.*\.google(?:mail)?\.com)$", x.lower() ) else False, 
                     exchanges ) ):
            return "Google" 

        # Is it hosted internally?
        if all( map( lambda x: x.find( self.url ) != -1, exchanges ) ):
            return "Internal"

        # Must Be Hosted Externally
        return "External"

    def _checkSpfMethod( self ):
        """
            Check SPF Methods
                NOT YET IMPLEMENTED
        """
        pass


    def reverseName( self ):
        """
                Return ARPA Reverse Name For RDNS Lookups, only returns
            first collected domain ip

            @return None   - No A Records Were Collected
            @return String - Arpa Reverse Name

            '''
                Sidenote: 
                   Remember palindromes? :P

                str = 'lol'
                assert str == str[::-1]
            '''

        """
        return None if self.a_records is None else "{}.in-addr.arpa".format( '.'.join( self.a_records[0].split('.')[::-1] ) )
