
class elasticsearch {

    #group {
    #    'ElasticSearch-ServiceGroup':
    #        ensure => present,
    #        system => true,
    #        name   => 'elasticsearch';
    #}

    user {
        'ElasticSearch-ServiceUser':
            ensure  => present,
            system  => true,
            name    => 'elasticsearch',
            comment => 'Elasticsearch Service User',
    #        require => Group[ 'ElasticSearch-ServiceGroup' ];
    }

    exec {
        'Download-ElasticSearch':
            command  => '/usr/bin/curl -LsO https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.deb',
            cwd      => '/root/pkgs',
            creates  => '/root/pkgs/elasticsearch-1.0.1.deb';
    
        #  Sadly upgrading here pulls new kernel during jre install
        # borking guest tools and making you a sad panda; We flush instead
        # in to drop our stale caches. (lame)
        #'Update-Repos':
        #    command  => '/usr/bin/apt-get update',
        #    require  => Exec[ 'Download-ElasticSearch' ];
    }

    package {
        'Java-RuntimeEnv':
            ensure   => installed,
            name     => 'openjdk-7-jre',
            require  => Exec[ 'Download-ElasticSearch' ];
            
        'ElasticSearch':
            ensure   => installed,
            provider => dpkg,
            source   => '/root/pkgs/elasticsearch-1.0.1.deb',
            require  => Package[ 'Java-RuntimeEnv' ];
    }

    File { owner => 'elasticsearch', group => 'elasticsearch' }
    # Config && Improved Init Script
    file {

        'Elastic-Config':
            ensure  => file,
            path    => '/etc/elasticsearch/elasticsearch.yml',
            source  => '/vagrant/etc/puppet/files/elasticsearch/elasticsearch.yml',
            mode    => 0600,
            require => Package[ 'ElasticSearch' ];

        'Elastic-InitScript':
            ensure  => file,
            path    => '/etc/init.d/elasticsearch',
            source  => '/vagrant/etc/puppet/files/elasticsearch/elasticsearch.init.d',
            mode    => 0750,
            require => File[ 'Elastic-Config' ];

    }

    # Enable at boot and start now
    service {
        'ElasticSearch':
            ensure     => running,
            name       => 'elasticsearch',
            enable     => true,
            hasstatus  => true,
            hasrestart => true,
            require    => File[ 'Elastic-InitScript' ];
    }
}
