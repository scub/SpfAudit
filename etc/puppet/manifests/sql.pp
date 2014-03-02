
class sql {

    # Install Our Server
    class { "postgresql::server": } -> 

    # Create SpfAudit Database And User
    postgresql::server::db {
        'SpfAudit':
            user     => 'vagrant',
            password => postgresql_password( 'vagrant', 'ThGK4E4!UxJOElzMq5RysiG6j' );
    }

}
