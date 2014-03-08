#!/usr/bin/python

from sm_Base import sm_Base

class sm_Elastic( sm_Base ):

    def __init__( self, screen, botMaster, throttle = 1 ):

        super( sm_Elastic, self ).__init__( screen      = screen,
                                            botMaster   = botMaster,
                                            botList     = "esBrokers", 
                                            menuName    = "JSON Broker",
                                            menuOptions = "(W)atch (S)tatus (P)rogress",
                                            throttle    = throttle )

        self.SIGNALS.update( {
            'w' : ( "VERBOSE", None ),
            'p' : ( "LPROC",   None ),
            's' : ( "ALL",     None ),
        } )

        self.view()
