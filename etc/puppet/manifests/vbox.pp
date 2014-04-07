
class vbox {

    exec {
        'Update Guest Utils':
            command => '/usr/bin/apt-get install -y virtualbox-guest-utils',
            timeout => 900,
            require => Exec[ 'Flush Stale Repo Cache' ];
    }

}
