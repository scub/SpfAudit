
class sql {

    # Install Our Server
    class { "postgresql::server": } -> 

    # Create SpfAudit Database And User
    postgresql::server::db {
        'SpfAudit':
            user     => 'ubuntu',
            password => postgresql_password( 'ubuntu', 'ThGK4E4!UxJOElzMq5RysiG6j' );
    } 

    # Python API
    package {
        'python-psycopg2': 
            ensure  => installed,
            require => Postgresql::Server::Db[ 'SpfAudit' ];

        'python-psycopg2-dbg':
            ensure  => installed,
            require => Package[ 'python-psycopg2' ];

        'python-psycopg2-doc':
            ensure  => installed,
            require => Package[ 'python-psycopg2-doc' ];
    }

}
