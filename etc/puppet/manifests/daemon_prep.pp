
class daemon_prep {

    Group { system => true }
    User  { system => true }

    # Service User Groups
    #group {
    #    'NGINX-ServiceGroup':
    #        ensure => present,
    #        name   => 'nginx';
    #}

    user {
        'NGINX-ServiceUser':
            ensure  => present,
            gid     => "nginx",
            name    => 'nginx',
            home    => '/usr/local/www',
            comment => 'Nginx Service User',
            #require => Group[ 'NGINX-ServiceGroup' ];
    }

    file {
        '/usr/local/www':
            ensure  => directory,
            owner   => 'nginx',
            group   => 'nginx',
            mode    => 0701,
            require => User[ 'NGINX-ServiceUser' ];

        '/root/pkgs':
            ensure  => directory,
            owner   => 'root',
            group   => 'root',
            mode    => 0701,
            require => File[ '/usr/local/www' ];
    }

    # Kibana
    exec {
        'Download-Kibana':
            command => '/usr/bin/curl -Lso /root/pkgs/kibana-3.0.0milestone5.tar.gz https://download.elasticsearch.org/kibana/kibana/kibana-3.0.0milestone5.tar.gz',
            creates => '/root/pkgs/kibana-3.0.0milestone5.tar.gz',
            require => File[ '/root/pkgs' ];

        'Extract-Kibana':
            command => '/bin/tar -zxvf /root/pkgs/kibana-3.0.0milestone5.tar.gz',
            cwd     => '/usr/local/www',
            creates => '/usr/local/www/kibana-3.0.0milestone5',
            require => Exec[ 'Download-Kibana' ]; 

        'Fix-Ownership':
            command => '/bin/chown -R nginx:nginx /usr/local/www',
            require => Exec[ 'Extract-Kibana' ];

        'Fix-Perms-Files':
            command => '/usr/bin/find /usr/local/www -type f -exec chmod 600 {} \;',
            require => Exec[ 'Fix-Ownership' ];

        'Fix-Perms-Dirs':
            command => '/usr/bin/find /usr/local/www -type d -exec chmod 701 {} \;',
            require => Exec[ 'Fix-Perms-Files' ];
    }

    file {
        'Kibana-config.js':
            ensure  => file,
            path    => '/usr/local/www/kibana-3.0.0milestone5/config.js',
            source  => '/vagrant/etc/puppet/files/kibana/config.js',
            owner   => 'nginx',
            group   => 'nginx',
            mode    => 0600,
            require => Exec[ 'Fix-Perms-Dirs' ];

        'Kibana-Dashboard.json':
            ensure  => file,
            path    => '/usr/local/www/kibana-3.0.0milestone5/app/dashboards/default.json',
            source  => '/vagrant/etc/puppet/files/kibana/default.json',
            owner   => 'nginx',
            group   => 'nginx',
            mode    => 0600,
            require => File[ 'Kibana-config.js' ];
    }
}
