#!/usr/bin/python3
import os

_local_only = False

test_phase = ['local', 'ssh', 'nfs']


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
