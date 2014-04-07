
class params {

    $virtualized => false;
    
    if $virtualized == false {
        $base_user  => 'ubuntu'
    } else {
        $base_user  => 'vagrant'
    }
}
