#!/usr/bin/python3
import os
import sys
from time import time, localtime

test_phase = ['local-only', 'local', 'ssh', 'nfs']
_EBAD = -1
_crash_dir = '/var/crash'
_ssh_remote_server = 'ubuntu@kdump-netcrash'
_nfs_remote_mountpoint = 'kdump-netcrash:/var/crash'

#
# Used to indicate that netdump tests
# should not be run (SSH & NFS)
#
_local_only = False


def trigger_crash():
    if crash_switch:
        try:
            f = open("/proc/sysrq-trigger", "a")
            f.write('c')
        except PermissionError as err:
            print("Must be root to trigger a crash dump\t{}".format(err))
    else:
        print("Would trigger a panic but crash_switch is False")


def create_ref_conf():
    try:
        with open("/etc/default/kdump-tools.ref", "r") as f:
            pass
    except FileNotFoundError:
        try:
            os.rename(
                "/etc/default/kdump-tools", "/etc/default/kdump-tools.ref")
        except PermissionError as err:
            print(("User does not have the privilege "
                   "to change this file\t{}").format(err))
            return _EBAD
    return


def set_conffile(test):
    with open("/etc/default/kdump-tools.ref", "r") as orig:
        try:
            if test == 'local' or test == 'local-only':
                with open("/etc/default/kdump-tools", "w") as new_conf:
                    for line in orig.readlines():
                        if line.find('USE_KDUMP') == 0:
                            new_conf.write("{}".format('USE_KDUMP=1\n'))
                        else:
                            new_conf.write("{}".format(line))
            elif test == 'ssh':
                ref = orig.read()
                orig.seek(0)
                if ref.find("SSH") != -1:
                    with open("/etc/default/kdump-tools", "w") as new_conf:
                        for line in orig.readlines():
                            if line.find('USE_KDUMP') == 0:
                                new_conf.write("{}".format('USE_KDUMP=1\n'))
                            else:
                                new_conf.write("{}".format(line))
                        new_conf.write('SSH="{}"\n'.format(_ssh_remote_server))
                else:
                    print("SSH functionality not found in {}".format(
                        '/etc/default/kdump-tools'))
                    return _EBAD
            elif test == 'nfs':
                ref = orig.read()
                orig.seek(0)
                if ref.find("NFS") != -1:
                    with open("/etc/default/kdump-tools", "w") as new_conf:
                        for line in orig.readlines():
                            if line.find('USE_KDUMP') == 0:
                                new_conf.write("{}".format('USE_KDUMP=1\n'))
                            else:
                                new_conf.write("{}".format(line))
                        new_conf.write('NFS="{}"\n'.format(_nfs_remote_mountpoint))
                        #
                        # Adding HOSTTAG to test the functionality
                        # And avoid name collision b/w SSH and NFS
                        #
                        new_conf.write('HOSTTAG="hostname"\n')
                else:
                    print("NFS functionality not found in {}".format(
                        '/etc/default/kdump-tools'))
                    return _EBAD
            else:
                raise TypeError("Invalid test")
        except PermissionError as err:
            print(("User does not have the privilege "
                   "to change this file\t{}").format(err))
            return _EBAD
    return


def run_test(test):
    f = open('/var/crash/next-test', 'w')
    if test == 'local':
        f.write('ssh\n')
        f.close()
        os.sync()
    elif test == 'ssh':
        f.write('nfs\n')
        f.close()
        os.sync()
    elif test == 'nfs' or test == 'local-only':
        f.write('completed\n')
        f.close()
        os.sync()
    else:
        raise TypeError("Invalid test")
    trigger_crash()
    return


def gather_test_results():
    print("Getting the results")
    pass


if __name__ == '__main__':

    if len(sys.argv) > 1:
        crash_switch = True
        pass
    else:
        crash_switch = False

    if create_ref_conf() == _EBAD:
        exit(_EBAD)

    try:
        f = open('/var/crash/next-test', 'r')
        phase = f.read().strip()
        f.close()
    except FileNotFoundError:
        if _local_only:
            phase = 'local-only'
        else:
            phase = 'local'
    print("Running phase {}".format(phase.upper()))
    if phase != 'completed':
        if set_conffile(phase) != _EBAD:
            run_test(phase)
        else:
            print("Unable to continue with tests")
            f = open('/var/crash/next-test', 'w')
            f.write('completed\n')
            f.close()
            exit(_EBAD)
    else:
        os.unlink('/var/crash/next-test')

    gather_test_results()
# vim: et ts=4 sw=4
