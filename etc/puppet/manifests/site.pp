import 'bootstrap'
import 'dev_env'
import 'daemon_prep'
import 'elasticsearch'
import 'nginx_env'
import 'sql'
import 'fwall'

#
#    Bootstrap Local vbox with minimal host
#
node 'ubuntu1310-i386' {

    include bootstrap, dev_env, daemon_prep, elasticsearch, nginx_env, sql, fwall

    $base_user = "ubuntu"

    Class[ 'bootstrap'   ] -> Class[ 'vbox'          ] -> Class[ 'dev_env'   ] -> 
    Class[ 'daemon_prep' ] -> Class[ 'elasticsearch' ] -> Class[ 'nginx_env' ] -> 
    Class[ 'sql'         ] -> Class[ 'fwall'         ]

}

#
#  To The Cloud!!! 
#
node /(^.*\.ec2\.internal$|^spf$|^spf\.aud\.it$)/ {

    include bootstrap, dev_env, daemon_prep, elasticsearch, nginx_env, sql, fwall

    $base_user = "ubuntu"

    Class[ 'bootstrap'     ] -> Class[ 'dev_env'   ] -> Class[ 'daemon_prep' ] ->
    Class[ 'elasticsearch' ] -> Class[ 'nginx_env' ] -> Class[ 'sql'         ] ->
    Class[ 'fwall'         ]

}
