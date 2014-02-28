import 'bootstrap'
import 'dev_env'

#
#    Bootstrap base box with minimal host
# information to boot on.
#
node 'ubuntu1310-i386' {
    include bootstrap 

    notify { 'Spam': message => 'Bootstrap successful, restarting guest machine for changes to take effect.' }
    exec   {
        'Trigger Restart':
            command => "/sbin/shutdown -r now",
            require => Class[ 'bootstrap' ]
    }

    Class[ 'bootstrap' ] -> Notify[ 'Spam' ] -> Exec[ 'Trigger Restart' ]
}

#   After Bootstrapping we install our dev
# environment, and then begin to deploy our 
# service set. [Nginx, ElasticSearch, Posgresql]
#
node 'spf' {

    include bootstrap, dev_env

}
