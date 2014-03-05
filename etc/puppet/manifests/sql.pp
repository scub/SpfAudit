
class sql {

    # Install Our Server
    class { "postgresql::server": } -> 

    # Create SpfAudit Database And User
    postgresql::server::db {
        'SpfAudit':
            user     => 'vagrant',
            password => postgresql_password( 'vagrant', 'ThGK4E4!UxJOElzMq5RysiG6j' );
    } ->

    # Python API
    package {
        [ 'python-psycopg2', 'python-psycopg2-dbg', 'python-psycopg2-doc' ]:
            ensure => installed;
    }

}
