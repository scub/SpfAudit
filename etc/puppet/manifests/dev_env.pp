#
#    Setup Development Environment, Including
# Required Dependencies.
#
#

class dev_env {

    # Global Templates
    Package { ensure => latest }
    File    { owner  => $base_user,  group => $base_user }

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

        'TMUX':
            name    => 'tmux',
            require => Package[ 'SETUPTOOLS' ];

        'PIP':
            name    => 'python-pip',
            require => Package[ 'TMUX' ]; 

        'SENDMAIL':
            name    => 'sendmail-bin',
            require => Package[ 'PIP' ];

        'PYLZMA':
            name    => 'python-lzma',
            require => Package[ 'SENDMAIL' ];
    }

    # Snatch External Libs and Geoip Database
    exec {

        'dnspython':
            command => "/usr/bin/pip install dnspython",
            require => Package[ 'PYLZMA' ]; 

        'geoip2':
            command => "/usr/bin/pip install geoip2",
            require => Exec[ 'dnspython' ];

        'iptools':
            command => "/usr/bin/pip install iptools",
            require => Exec[ 'geoip2' ];

        'Elastic-py':
            command => "/usr/bin/pip install elasticsearch",
            require => Exec[ 'iptools' ];
            
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
            command => "/bin/chown -R $base_user:$base_user /usr/share/geoip",
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

        'TMUX.CONF':
            ensure => file,
            path   => "/etc/tmux.conf",
            source => "/vagrant/etc/puppet/files/host/tmux.conf";

        'Bashrc':
            ensure => file,
            path   => "/home/$base_user/.bashrc",
            source => "/vagrant/etc/puppet/files/host/bashrc";

    }
}
