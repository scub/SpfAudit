# SPF Audit 
#
# BaseBox
# -------
#
#   Ubuntu Server 13.10 
#       http://puppet-vagrant-boxes.puppetlabs.com/ubuntu-1310-i386-virtualbox-puppet.box 
#
#   ALT: CentOS 6.4 i386 Minimal ( Chef 11.6.0, Puppet 3.2.3 )  [ No Native Py 2.7 ]
#       http://developer.nrel.gov/downloads/vagrant-boxes/CentOS-6.4-i386-v20130731.box
#
#   ALT: CentOS 6.5 i386 ( Puppet 3.2.3 ) [ No Native Py 2.7 ]
#       http://puppet-vagrant-boxes.puppetlabs.com/centos-65-i386-virtualbox-puppet.box
#

Vagrant.configure( "2" ) do |config|

  config.vm.box     = "SPF-Audit-Buntu"
  config.vm.box_url = "http://puppet-vagrant-boxes.puppetlabs.com/ubuntu-1310-i386-virtualbox-puppet.box"

  # Forwards, Kibana - Nginx Forward 
  config.vm.network :forwarded_port, guest: 80, host: 8989

  # VirtualBox, Gross... 
  config.vm.provider :virtualbox do |vb|
   # Beef up the ram to 1Gb
   vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
  
  # PUPPET, RAWRRRR! 
  config.vm.provision :puppet do |puppet|

    puppet.manifests_path    = "etc/puppet/manifests"
    puppet.manifest_file     = "site.pp"
    puppet.working_directory = "/tmp/vagrant-puppet/manifests"

  end

end
