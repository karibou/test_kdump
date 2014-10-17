#!/usr/bin/python3
import os
import sys
from time import time, localtime

test_phase = ['local-only', 'local', 'ssh', 'nfs']
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


def add_ref_conf():
    try:
        with open("/etc/default/kdump-tools.ref", "r") as f:
            pass
    except FileNotFoundError:
        with open("/etc/default/kdump-tools", "r") as orig:
            try:
                ref = open("/etc/default/kdump-tools.ref", "w")
                for line in orig.readlines():
                    ref.write(line)
                ref.close()
            except PermissionError as err:
                print("Must be root to trigger a crash dump\t{}".format(err))
        orig.close()
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
        if len(dirs) != 0 and dirs[0].find(str(now.tm_year)) == 0 :
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

if __name__ == '__main__':

    if len(sys.argv) > 1:
        crash_switch = True
        pass
    else:
        crash_switch = False

    add_ref_conf()

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

# vim: et ts=4 sw=4
