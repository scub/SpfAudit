class bootstrap {

    File { owner => root, group => root, mode => 0644 }

    package { 'tzdata': ensure => present }

    file { 
        '/etc/timezone':
            path    => '/etc/timezone',
            content => 'Etc/UTC',
            require => Package[ 'tzdata' ];

        '/etc/localtime':
            ensure  => link,
            path    => '/etc/localtime',
            target  => '/usr/share/zoneinfo/UTC',
            require => File[ '/etc/timezone' ];

        '/etc/hostname':
            content => 'spf.aud.it',
            require => File[ '/etc/localtime' ];

        '/etc/hosts':
            content => "127.0.0.1 localhost.localdomain localhost spf spf.aud.it\n::1 localhost6 spf6.aud.it",
            require => File[ '/etc/hostname' ];

        '/etc/resolv.conf':
            content => "search aud.it\nnameserver 8.8.8.8",
            require => File[ '/etc/hosts' ];

        '/etc/motd':
            content => "\n
      ██████  ██▓███   █████▒    ▄▄▄       █    ██ ▓█████▄  ██▓▄▄▄█████▓
    ██    ▒ ▓██░  ██▒▓██   ▒    ▒████▄     ██  ▓██▒▒██▀ ██▌▓██▒▓  ██▒ ▓▒
     ▓██▄   ▓██░ ██▓▒▒████ ░    ▒██  ▀█▄  ▓██  ▒██░░██   █▌▒██▒▒ ▓██░ ▒░
     ▒   ██▒▒██▄█▓▒ ▒░▓█▒  ░    ░██▄▄▄▄██ ▓▓█  ░██░░▓█▄   ▌░██░░ ▓██▓ ░ 
    ██████▒▒▒██▒ ░  ░░▒█░        ▓█   ▓██▒▒▒█████▓ ░▒████▓ ░██░  ▒██▒ ░ 
     ▒▓▒ ▒ ░▒▓▒░ ░  ░ ▒ ░        ▒▒   ▓▒█░░▒▓▒ ▒ ▒  ▒▒▓  ▒ ░▓    ▒ ░░   
     ░▒  ░ ░░▒ ░      ░           ▒   ▒▒ ░░░▒░ ░ ░  ░ ▒  ▒  ▒ ░    ░    
      ░  ░  ░░        ░ ░         ░   ▒    ░░░ ░ ░  ░ ░  ░  ▒ ░  ░      
         ░                            ░  ░   ░        ░     ░           
                                                            ░\n\n\n
                [ Lets Play Poke The Internets! ]\n\n\n",
            require => File[ "/etc/resolv.conf" ];
    }

    exec {
        'Set Hostname':
            command => "/bin/hostname -F /etc/hostname",
            require => File[ '/etc/motd' ];
    }

}
