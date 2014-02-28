
class daemon_prep {

    Group { system => true }
    User  { system => true }

    # Service User Groups
    group {

        'NGINX-ServiceGroup':
            ensure => present,
            name   => 'nginx';

        'ElasticSearch-ServiceGroup':
            ensure => present,
            name   => 'elasticsearch';
    }

    user {

        'NGINX-ServiceUser':
            ensure  => present,
            name    => 'nginx',
            home    => '/usr/local/www',
            comment => 'Nginx Service User',
            require => Group[ 'NGINX-ServiceGroup' ];

        'ElasticSearch-ServiceUser':
            ensure  => present,
            name    => 'elasticsearch',
            comment => 'Elasticsearch Service User',
            require => Group[ 'ElasticSearch-ServiceGroup' ];

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

        '/opt/elasticsearch':
            ensure  => directory,
            owner   => 'elasticsearch',
            group   => 'elasticsearch',
            mode    => 0701,
            require => File[ '/root/pkgs' ];
    }

    # Kibana
    exec {
        'Download-Kibana':
            command => '/usr/bin/curl -Lso /root/pkgs/kibana-3.0.0milestone5.tar.gz https://download.elasticsearch.org/kibana/kibana/kibana-3.0.0milestone5.tar.gz',
            creates => '/root/pkgs/kibana-3.0.0milestone5.tar.gz',
            require => File[ '/opt/elasticsearch' ];

        'Extract-Kibana':
            command => '/bin/tar -zxvf /root/pkgs/kibana-3.0.0milestone5.tar.gz',
            cwd     => '/usr/local/www',
            creates => '/usr/local/www/kibana-3.0.0milestone5.tar.gz',
            require => Exec[ 'Download-Kibana' ]; 

        'Fix-Ownership':
            command => '/bin/chown -R nginx:nginx /usr/local/www',
            require => Exec[ 'Extract-Kibana' ];

        'Fix-Perms':
            command => '/usr/bin/find /usr/local/www/ -type f -exec chmod 600 {} \;',
            require => Exec[ 'Fix-Ownership' ];
    }

    # Postgresql

    #
}
