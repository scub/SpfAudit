#!/usr/bin/python

from sm_Base import sm_Base

class sm_Sql( sm_Base ):

    def __init__( self, screen, botMaster, throttle = 1 ):

        super( sm_Sql, self ).__init__( screen      = screen,
                                            botMaster   = botMaster,
                                            botList     = "sqlBrokers", 
                                            menuName    = "SQL Broker",
                                            menuOptions = "(W)atch (S)tatus (P)rogress",
                                            throttle    = throttle )

        self.SIGNALS.update( {
            'w' : ( "VERBOSE", None ),
            'p' : ( "LPROC",   None ),
            's' : ( "ALL",     None ),
        } )

        self.view()
