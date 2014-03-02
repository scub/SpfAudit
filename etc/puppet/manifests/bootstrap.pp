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
            content => "127.0.0.1 spf.aud.it spf localhost.localdomain localhost\n::1 spf6.aud.it spf6 localhost6.localdomain localhost6\n",
            require => File[ '/etc/hostname' ];

        '/etc/resolv.conf':
            content => "search aud.it\nnameserver 8.8.8.8\n",
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

    # Set Hostname Install Auxiliary Modules
    exec {
        'Set Hostname':
            command => "/bin/hostname -F /etc/hostname",
            require => File[ '/etc/motd' ];

        'Puppetlabs-Postgresql':
            command => "/usr/bin/puppet module install puppetlabs-postgresql --modulepath /etc/puppet/modules",
            creates => "/etc/puppet/modules/postgresql",
            require => Exec[ 'Set Hostname' ];

        'Freeze Kernel':
            command => '/vagrant/etc/sbin/freeze_kernel.sh',
            require => Exec[ 'Puppetlabs-Postgresql' ];

        'Flush Stale Repo Cache':
            command => '/usr/bin/apt-get update && /usr/bin/apt-get upgrade -y',
            require => Exec[ 'Freeze Kernel' ];
    }
}
