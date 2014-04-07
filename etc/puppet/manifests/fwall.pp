
class fwall {

    class     { 'firewall': } 

    resources { 'firewall': purge => true, require => Class[ 'firewall' ]; } 

    firewall  {
            
        "000 ICMP":
            proto   => "icmp",
            action  => "accept",
            require => Resources[ 'firewall' ];

        "001 Loopback":
            proto   => "all",
            iniface => "lo",
            action  => "accept",
            require => Firewall[ '000 ICMP' ];

        "002 Established Connections":
            proto   => "all",
            ctstate => [ 'RELATED', 'ESTABLISHED' ],
            action  => "accept",
            require => Firewall[ '001 Loopback' ];

        "003 Nginx - HTTPD":
            proto   => "tcp",
            ctstate => [ 'NEW'       ],
            port    => [ '80', '443' ],
            action  => "accept",
            require => Firewall[ '002 Established Connections' ]; 

        "004 OpenSSH - SSHD":
            proto   => "tcp",
            ctstate => [ 'NEW' ],
            port    => [ '22'  ],
            action  => "accept",
            require => Firewall[ '003 Nginx - HTTPD' ];

        "999 Reject All Traffic":
            proto   => "all",
            ctstate => [ 'NEW' ],
            action  => "reject",
            require => Firewall[ '004 OpenSSH - SSHD' ]; 

    }
}
