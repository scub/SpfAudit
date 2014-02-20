#!/usr/bin/python

from lib.CommandAndControl import CommandAndControl
from lib.menus.Master      import MainMenu as Interactive
from lib.types.node        import Node

def targeting():
    for i in range( 125, 150 ):
        yield Node( a_records = [ "96.126.107.{}".format( i ) ] )

Interactive( CommandAndControl, 1, "var/log/test_MainMenu.log", targeting )
