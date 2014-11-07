test_kdump
==========

Introduction
------------

This set of scripts is intended to test the kdump-tools scripts responsible
for the generation of kernel crash dumps.

One instance called *kdump-netcrash* is expected to exist and be reachable by
the *test-kdump* instance.  The *kdump-netcrash* cloud-config script should be
sufficient to instantiate it.

Once the *kdump-netcrash* instance is ready to receive the networked dumps, a
second instance is started which will complete its configuration and reboot 
to run the tests.


Local-only tests
----------------

If the user do not want to run the networked kernel dump functionalities, then
the environment variable LOCAL_ONLY needs to be set to 1. In that case, the
*kdump-netcrash* instance is not required and only local tests will be performed.

Test Result Analysis
====================

The default behavior is to run a crash session on each of the generated crash dump to
confirm that the kernel crash dumps gathered are valid. This is a lengthy process as
the test script must download the kernel with debug symbols from the archive. This
package is over 300Mb so it can take time.

It is possible to override this phase and only run the crash tests by setting up the
NO_RESULT environment variable to 1. This will tell the script not to run the result
verification phase.

Variable pre-definition in default file
=======================================
It is possible to define the environment variables described above in a file called
/etc/default/kdump-test-script. The file is read upon startup and if it exists, it
will define the environment variable to be used.
Theory of operation
-------------------

The cloud-config script is responsible for enabling kernel dump on the instance. It
then download the python test script called *kdump-test-script.py* from the internet
and stores it in /etc/init.d. A link is created at run-level 2 so the test script is
run at the end of the boot.

The script will adapt the configuration file /etc/default/kdump-tools to the expected
test (local, ssh or nfs) and trigger a kernel panic.  It will also create a temporary
file called *next-test* in /var/crash that will indicate which test should be run next.
The script will then trigger a kernel panic. The panic will exercise the kdump 
functionality and will then reboot. Upon reboot, the next test in sequence will be 
configured and a new panic will be triggered.

At the end of the set of test or if *_local_only* is set to True, the tests results will
be copied into the /var/crash of the *test-kdump* instance if networked tests are 
done, and each test directory will be prefixed with the type of test performed.


The script assumes that the remote instance is called kdump-netcrash and has 
a ubuntu user.  This can be modified in the .py script.

The cloud instance script test-kdump suppose that the kdump-test-script.py is
available for download at the given URL. This also can easily be changed before
starting the instance

The kdump-tools version to be tested is the one available from the archive 
configuration when the kdump-test instance is configured. A PPA can be used
to test specific versions.

Those are very brief instructions. A more detailed description will (hopefully)
become available soon.


Steps to run the tests
======================

The ssh keys only need to be added when the cloud-config scripts are created
for the first time :

    ssh-keygen kdump_id_rsa

Add the private key to kdump-test
Add the public key to kdump-netcrash

Create the kdump-netcrash instance 

    $ uvt-kvm create kdump-netcrash release=trusty arch=amd64 --user-data kdump-netcrash

Once kdump-netcrash has finished its setup; start the second instance that will run the tests

    $ uvt-kvm create test-kdump release=trusty arch=amd64 --user-data test-kdump

