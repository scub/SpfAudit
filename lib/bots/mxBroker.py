#!/usr/bin/python

# Python Natives
from   smtplib    import SMTP, SMTPRecipientsRefused, SMTPHeloError
from   smtplib    import SMTPSenderRefused, SMTPDataError
from   Queue	  import Empty as QueueEmpty

# Custom Types
from   brokerBase import brokerBase

class mxBroker( brokerBase ):
    """
        mxBroker

            This broker acts as an intermediary to communicate
         with other exchanges using a MTA. Records are fed through
         a queued interface and automatically processed; An Alert
         is sent to the administrator of a given node object if
         that node is found to be vulnerable.
    """

    def __init__( self,
                  workerId,
                  logPath,
                  qin      = None,
                  metaQin  = None,
                  metaQout = None,
                  geoip    = None ):
        """
            Create new mxBroker instance.

            @param Int    workerId  - Worker Identification Number
            @param String logPath   - Logging Path
            @param Queue  qin       - Processing Queue
            @param Queue  metaQin   - Requests for stats/run state 
            @param Queue  metaQout  - Responses to requests for runstate
        """
        super( mxBroker, self ).__init__( 
            workerId       = workerId,
            workerPurpose  = 'mxBroker',
            logPath        = logPath,
            qin            = qin,
            metaQin        = metaQin,
            metaQout       = metaQout
        )

        self.state.update( {

            'sender' : "alerts@spf.aud.it",

            'alive'  : True,
            'smtp'   : SMTP( 'localhost' ),
        } )

        self.state[ 'smtp' ].set_debuglevel( 1 )

    def _alert( self, node ):
        """
            Given a node object alert the administrator that
            they should really implement spf records for their
            organization.
            
            @param Node node - Node object contains aggregated host information
        """
        
        Message = """
        Good Day Sir/Madam,

            This message was generated to inform you that your mx infrastructure allows
        unverified users to masquerade as any member of your organization. This is
        largely due to a lack of spf records attached to the domain "{0}". To mitigate this
        issue configuring your Sender Policy Framework through the use of TXT records, exposed
        by DNS.

            A very simple yet effective spf record to lock down email so that its only sent from
        the ip's that {0} resolves to is attached below in the hopes that it will aid you in the 
        securing of these forward facing assets.

        "v=spf1 a:{0} -all"

           Further reading about the Sender Policy Framework, and how it can be used can be found
        at the opensource spf organizations homepage: http://www.openspf.org
        """.format( node.url )

        self._spam( self.state[ 'sender' ], "root@{}".format(  node.url ), Message )

    def _spam( self, sender, recpt, message );
        """
              Send email to given user using given name

              @param String sender  - Address to send from
              @param String recpt   - Recipient of email
              @param String message - Message to relay
        """
        try:
            self.state[ 'smtp' ].sendmail( sender, recpt, message )
        except SMTPRecipientsRefused as EmailIgnored:
            self._log( 'alert', 'DEBUG', 'SMTP Recipient Refused {}'.format( node.url ) )
        except SMTPHeloError as ExchangeError:
            self._log( 'alert', 'CRITICAL', 'Failed handshake, possible issues with sendmail' )
        except SMTPSenderRefused as AuthenticationError:
            self._log( 'alert', 'CRITICAL', 'User does not have required permissions to send email' )
        except SMTPDataError as MalformedEmail:
            self._log( 'alert', 'CRITICAL', 'Email malformed {}'.format( node.url ) )

    def process( self, node ):
        """
            Given a node object, check for vulnerability and alert
            administrator of any required actions.

            @param Node node - Node object contains aggregated host information
        """
        if type( node ) == str: return

        if not all( map( lambda x: x is not None,
                         [ node.url, node.a_records, node.mx_recodrs ] ) ): return

        # If Hosted Through Google Running With Open Or No SPF
        if node._checkMxHosted() == "Google" and node._checkSpfMethod() in [ "None", "Pass" ]:

            # Alert administrator
            self.alert( node )


    def __del__( self ):
        """
            clean up our server connections before exiting
        """
        self.state[ 'smtp' ].close()
