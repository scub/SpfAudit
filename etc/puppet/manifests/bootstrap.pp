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
        
        'Puppetlabs-Stdlib':
            command => "/usr/bin/puppet module install puppetlabs-stdlib",
            creates => "/etc/puppet/modules/stdlib",
            cwd     => "/etc/puppet/modules/",
            require => Exec[ 'Set Hostname' ];

        'Puppetlabs-Firewall':
            command => "/usr/bin/puppet module install puppetlabs-firewall",
            creates => "/etc/puppet/modules/firewall",
            cwd     => "/etc/puppet/modules/",
            require => Exec[ 'Puppetlabs-Stdlib' ];

        'Puppetlabs-Apt':
            command => "/usr/bin/puppet module install puppetlabs-apt",
            creates => "/etc/puppet/modules/apt",
            cwd     => "/etc/puppet/modules/",
            require => Exec[ 'Puppetlabs-Firewall' ];

        'Ripienaar-Concat':
            command => "/usr/bin/puppet module install ripienaar-concat",
            creates => "/etc/puppet/modules/concat",
            cwd     => "/etc/puppet/modules/",
            require => Exec[ 'Puppetlabs-Apt' ];

        'Puppetlabs-Postgresql':
            command => "/usr/bin/puppet module install puppetlabs-postgresql --version 2.5.0",
            creates => "/etc/puppet/modules/postgresql",
            cwd     => "/etc/puppet/modules/",
            require => Exec[ 'Ripienaar-Concat' ];

        'Flush Stale Repo Cache':
            command => '/usr/bin/apt-get update && /usr/bin/apt-get upgrade -y',
            timeout => 1200,
            require => Exec[ 'Puppetlabs-Postgresql' ];

    }
}
