#!/usr/bin/python

from sm_brokerBase import sm_brokerBase

class sm_SQL( sm_brokerBase ):

    def __init__( self, option = None, CommandAndControl = None ):

        super( sm_SQL, self ).__init__(
            CommandAndControl = CommandAndControl,
            botList           = 'sqlBrokers',
            menuName          = 'SQL Brokers',
        )
