# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "precise64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network :private_network, ip: "192.168.2.101"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/var/www/rwrapper"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider :virtualbox do |vb|
    # Don't boot with headless mode
    vb.gui = true
  
    # Use VBoxManage to customize the VM. For example to change memory:
    vb.customize ["modifyvm", :id, "--memory", "2048"]
  end

  config.vm.provision :shell do |sh|
    sh.inline = <<-EOF
      export DEBIAN_FRONTEND=noninteractive;
      apt-get update --assume-yes;
      apt-get install --assume-yes python-software-properties;
      add-apt-repository --yes ppa:rethinkdb/ppa 2>&1;
      apt-get update --assume-yes;
      apt-get install --assume-yes rethinkdb;

      sed -e 's/somebody/root/g' -e 's/somegroup/root/g' -e 's/# bind=127.0.0.1/bind=all/g' /etc/rethinkdb/default.conf.sample > /etc/rethinkdb/instances.d/default.conf

      rethinkdb create -d /var/lib/rethinkdb/instances.d/default 2>&1;

      service rethinkdb start;
    EOF
  end
end