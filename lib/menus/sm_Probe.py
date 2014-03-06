#!/usr/bin/python

from sm_Base import sm_Base

class sm_Probe( sm_Base ):

    def __init__( self, screen, botMaster, throttle = 1 ):

        super( sm_Probe, self ).__init__( screen      = screen,
                                          botMaster   = botMaster,
                                          menuName    = "DNS Probe",
                                          menuOptions = "(W)atch (S)tatus (P)rogress",
                                          throttle    = throttle )

        self.SIGNALS.update( {
            'w' : ( "VERBOSE", None ),
            'p' : ( "LPROC",   None ),
            's' : ( "ALL",     None )
        } )

        self.view()
