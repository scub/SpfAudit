#!/usr/bin/python

from sm_brokerBase import sm_brokerBase

class sm_Dns( sm_brokerBase ):

    def __init__( self, option = None, CommandAndControl = None ):

        super( sm_Dns, self ).__init__(
            CommandAndControl = CommandAndControl,
            botList           = 'workers',
            menuName          = 'DNS Probes',
        )

if __name__ == '__main__':
    class CNC( object ):
        def __init__( self ):
            return

    cnc = CNC()
    x = sm_Dns( CommandAndControl = cnc )
