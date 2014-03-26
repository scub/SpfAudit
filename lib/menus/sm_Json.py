#!/usr/bin/python

from sm_brokerBase import sm_brokerBase

class sm_Json( sm_brokerBase ):

    def __init__( self, option = None, CommandAndControl = None ):

        super( sm_Json, self ).__init__(
            CommandAndControl = CommandAndControl,
            botList           = 'esBrokers',
            menuName          = 'JSON Brokers',
        )
