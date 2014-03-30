#!/usr/bin/python

from sm_brokerBase import sm_brokerBase

class sm_Mx( sm_brokerBase ):

    def __init__( self, option = None, CommandAndControl = None ):

        super( sm_Mx, self ).__init__(
            CommandAndControl = CommandAndControl,
            botList           = 'mxBrokers',
            menuName          = 'Mx Broker',
        )
