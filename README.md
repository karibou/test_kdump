test_kdump
==========

The script assumes that the remote instance is called kdump-netcrash and has 
a ubuntu user.  This can be modified in the .py script.

The cloud instance script test-kdump suppose that the kdump-test-script.py is
available for download at the given URL. This also can easily be changed before
starting the instance

Those are very brief instructions. A more detailed description will (hopefully)
become available soon.


Steps to run the tests :

The ssh keys only need to be added when the cloud-config scripts are created
for the first time :

    ssh-keygen kdump_id_rsa

Add the private key to kdump-test
Add the public key to kdump-netcrash

Create the kdump-netcrash instance 

    $ uvt-kvm create kdump-netcrash release=trusty arch=amd64 --user-data kdump-netcrash

Once kdump-netcrash has finished its setup; start the second instance that will run the tests

    $ uvt-kvm create test-kdump release=trusty arch=amd64 --user-data test-kdump

