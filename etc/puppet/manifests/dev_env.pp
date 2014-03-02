#
#    Setup Development Environment, Including
# Required Dependencies.
#
#
class dev_env {

    # Global Templates
    Package { ensure => latest }
    File    { owner  => vagrant,  group => vagrant }

    file {
        'Geoip Data':
            ensure => directory,
            path   => "/usr/share/geoip",
            mode   => 755;
    }

    # Pull down a few packages to make our lives easier
    package {

        'VIM':
            name    => 'vim',
            require => File[ 'Geoip Data' ];

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

        'Elastic-py':
            command => "/usr/bin/pip install elasticsearch",
            require => Exec[ 'geoip2' ];

        'download-geoip-database':
            command => "/usr/bin/curl -Lso /tmp/GeoLite2-City.mmdb.gz http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz", 
            creates => "/tmp/GeoLiteCity.dat.gz",
            require => Exec[ 'Elastic-py' ];

        # Moved From /vagrant/etc due to issues with py2.7 mmap.mmap()
        # on a virtualized environment when used on a mounted directory
        'extract-geoip-databases':
            command => "/bin/gunzip -c /tmp/GeoLite2-City.mmdb.gz > /usr/share/geoip/GeoLite2-City.mmdb",
            creates => "/usr/share/geoip/GeoLite2-City.mmdb",
            require => Exec[ 'download-geoip-database' ];

        'set-perms-geoip':
            command => "/bin/chown -R vagrant:vagrant /usr/share/geoip",
            require => Exec[ 'extract-geoip-databases' ];
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
