
class nginx_env {

    package {
        'nginx':
            ensure => installed,
            name   => 'nginx-full';
    }

    File { owner => 'nginx', group => 'nginx' }
    file {
        'Nginx-Base-Config':
            ensure  => file,
            path    => "/etc/nginx/nginx.conf",
            source  => "/vagrant/etc/puppet/files/nginx/nginx-Base.conf",
            require => Package[ 'nginx' ];

        'Nginx-Kibana-Vhost':
            ensure  => file,
            path    => "/etc/nginx/conf.d/default.conf",
            source  => "/vagrant/etc/puppet/files/nginx/nginx-Kibana.conf",
            require => File[ 'Nginx-Base-Config' ];

        'Nginx-Kibana-Htpasswd':
            ensure  => file,
            path    => "/etc/nginx/conf.d/spf.aud.it.htpasswd",
            source  => "/vagrant/etc/puppet/files/nginx/spf.aud.it.htpasswd",
            require => File[ 'Nginx-Kibana-Vhost' ];
    }


    service {

        'Nginx':
            ensure     => running,
            name       => 'nginx',
            hasstatus  => true,
            hasrestart => true,
            require    => File[ 'Nginx-Kibana-Htpasswd' ];

   } 
} 
