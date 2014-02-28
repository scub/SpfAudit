#
#    Setup Development Environment, Including
# Required Dependencies.
#
#
class dev_env {

    # Global Templates
    Package { ensure => latest }
    File    { owner  => vagrant,  group => vagrant }

    # Pull down a few packages to make our lives easier
    package {

        'VIM':
            name    => 'vim';

        'GIT':
            name    => 'git-core',
            require => Package[ 'VIM' ];

        'SETUPTOOLS':
            name    => 'python-setuptools',
            require => Package[ 'GIT' ];

        'PIP':
            name    => 'python-pip',
            require => Package[ 'SETUPTOOLS' ];

    }

    # Snatch External Libs and Geoip Database
    exec {

        'dnspython':
            command => "/usr/bin/pip install dnspython",
            require => Package[ 'PIP' ]; 

        'geoip2':
            command => "/usr/bin/pip install geoip2",
            require => Exec[ 'dnspython' ];

        'download-geoip-database':
            command => "/usr/bin/curl -Lso /tmp/GeoLite2-City.mmdb.gz http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz", 
            creates => "/tmp/GeoLiteCity.dat.gz",
            require => Exec[ 'geoip2' ];

        'extract-geoip-databases':
            command => "/bin/gunzip -c /tmp/GeoLite2-City.mmdb.gz > /vagrant/etc/GeoLite2-City.mmdb",
            creates => "/vagrant/etc/GeoLite2-City.mmdb",
            require => Exec[ 'download-geoip-database' ];

        # SNATCH MX CSV DATA
    }

    # Setup Sym-links for our auditing cases
    file {

        'Audit-Lib':
            ensure => link,
            path   => "/vagrant/var/audit/lib",
            target => "/vagrant/lib";

        'Audit-Var':
            ensure => link,
            path   => "/vagrant/var/audit/var",
            target => "/vagrant/var";

        'Audit-Etc':
            ensure => link,
            path   => "/vagrant/var/audit/etc",
            target => "/vagrant/etc";

    }
}