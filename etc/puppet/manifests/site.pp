import 'bootstrap'
import 'dev_env'
import 'daemon_prep'
import 'elasticsearch'
import 'nginx_env'
import 'sql'
import 'fwall'

#
#    Bootstrap base box with minimal host
# information to boot on.
#
node 'ubuntu1310-i386' {
    include bootstrap 

    notify { 'Spam': message => 'Bootstrap successful, run vagrant reload so that all changes take effect.' }

    Class[ 'bootstrap' ] -> Notify[ 'Spam' ] 
}

#   After Bootstrapping we install our dev
# environment, and then begin to deploy our 
# service set. [Nginx, ElasticSearch, Posgresql]
#
node 'spf' {

    include bootstrap, dev_env, daemon_prep, elasticsearch, nginx_env, sql, fwall

    Class[ 'bootstrap'     ] -> Class[ 'dev_env'   ] -> Class[ 'daemon_prep' ] ->
    Class[ 'elasticsearch' ] -> Class[ 'nginx_env' ] -> Class[ 'sql'         ] ->
    Class[ 'fwall'         ]

}
