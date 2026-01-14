# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu2204"
  config.vm.box_version = "4.3.12"

  config.vm.provider "libvirt" do |lv|
    lv.memory = 2048
    lv.cpus = 2
  end

  config.vm.define "backend" do |backend|
    backend.vm.network "private_network", ip: "192.168.56.2"
    backend.vm.hostname = "backend"
  end
end
