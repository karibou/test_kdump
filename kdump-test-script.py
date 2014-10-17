#!/usr/bin/python3
import os
import sys
from time import time, localtime

test_phase = ['local-only', 'local', 'ssh', 'nfs']
_EBAD = -1
_crash_dir = '/var/crash'

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
            os.rename("/etc/default/kdump-tools", "/etc/default/kdump-tools.ref")
        except PermissionError as err:
            print("User does not have the privilege to change this file\t{}".format(err))
            return _EBAD
    return


def set_conffile(test):
    if test == 'ssh':
        pass
    elif test == 'nfs':
        pass
    else:
        raise TypeError("Invalid test")
    return


def rename_crash(label):
    now = localtime(time())
    for path, dirs, files in os.walk(_crash_dir):
        if len(dirs) != 0 and dirs[0].find(str(now.tm_year)) == 0:
            os.rename(
                '{}/{}'.format(_crash_dir, dirs[0]),
                '{}/{}_{}'.format(_crash_dir, label, dirs[0]))
            for file in files:
                if file.find(str('linux')) == 0:
                    os.rename(
                        '{}/{}'.format(_crash_dir, file),
                        '{}/{}_{}'.format(_crash_dir, label, file))


def run_test(test):
    f = open('/var/crash/next-test', 'w')
    if test == 'local':
        f.write('ssh\n')
        f.close()
        os.sync()
    elif test == 'ssh':
        rename_crash('ssh')
        f.write('nfs\n')
        f.close()
        os.sync()
    elif test == 'nfs' or test == 'local-only':
        rename_crash('nfs')
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
    except FileNotFoundError:
        if _local_only:
            phase = 'local-only'
        else:
            phase = 'local'
    print("Phase : {}".format(phase))
    if phase != 'completed':
        run_test(phase)
    else:
        os.unlink('/var/crash/next-test')

    gather_test_results()
# vim: et ts=4 sw=4
