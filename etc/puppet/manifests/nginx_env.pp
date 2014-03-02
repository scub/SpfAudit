
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
    }


    service {

        'Nginx':
            ensure     => running,
            name       => 'nginx',
            hasstatus  => true,
            hasrestart => true,
            require    => File[ 'Nginx-Kibana-Vhost' ];

   } 
} 
