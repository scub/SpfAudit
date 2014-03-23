#!/usr/bin/python

from brokerBase import brokerBase

class sm_Json( brokerBase ):

    def __init__( self, option = None, CommandAndControl = None ):

        super( sm_Json, self ).__init__(
            CommandAndControl = CommandAndControl,
            botList           = 'esBrokers',
            menuName          = 'JSON Brokers',
        )
