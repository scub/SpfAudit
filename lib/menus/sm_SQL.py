#!/usr/bin/python

from brokerBase import brokerBase

class sm_SQL( brokerBase ):

    def __init__( self, option = None, CommandAndControl = None ):

        super( sm_SQL, self ).__init__(
            CommandAndControl = CommandAndControl,
            botList           = 'sqlBrokers',
            menuName          = 'SQL Brokers',
        )
