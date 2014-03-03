#!/usr/bin/python

# Stdlib
from argparse              import ArgumentParser

# External dependencies
from lib.CommandAndControl import CommandAndControl
from lib.menus.Master      import MainMenu as Interactive
from lib.types.node        import Node


def targeting():
    """
        Pull our benchmarking data
    """
    with open( "etc/dom_bench.txt", "r" ) as fd:
        for line in fd:
            yield Node( url = line.strip() )

    # Lets Throw Some Ips In the mix for good measure
    for i in range( 0, 10 ):
        yield Node( a_records = [ "96.126.107.14{}".format( i ) ] )


if __name__ == '__main__':

    parser = ArgumentParser( description = "CmpSc 294 - Final Proposal [ SPF.AUD.IT ]" )

    parser.add_argument( '-w', '--workers', dest = 'wcount',  default = None,
                         help = "Worker Count" )

    parser.add_argument( '-e', '--eBroker', dest = 'ecount',  default = 3,
                         help = "Json Broker Count" )

    parser.add_argument( '-g', '--geoip',   dest = 'geoPath', default = None,
                         help = "GeoIP Database Path, If available. (MaxMind.mmdb)" )

    parser.add_argument( '-l', '--log',     dest = 'logPath', default = 'var/log/gmx_search.log', 
                         help = "Log File Path" )

    args = parser.parse_args()

    if not all( map( lambda x: x is not None, [ args.wcount, args.logPath ] ) ):
        parser.print_help()
        exit( -1 )

    Interactive( CommandAndControl, args.wcount, args.logPath, args.geoPath, targeting )

    print "Finished Host Results" 
