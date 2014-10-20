test_kdump
==========

Steps to run the tests :

ssh-keygen kdump_id_rsa

Add the private key to kdump-test
Add the public key to kdump-netcrash

  $ uvt-kvm create kdump-netcrash release=trusty arch=amd64 --user-data kdump-netcrash
  $ uvt-kvm create test-kdump release=trusty arch=amd64 --user-data test-kdump

