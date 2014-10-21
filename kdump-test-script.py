#!/usr/bin/python3
import os
import sys
import subprocess
import socket
from time import time, localtime, sleep

_EBAD = -1
_crash_dir = '/var/crash'
_next_phase = '{}/next-test'.format(_crash_dir)
_remote_server = 'kdump-netcrash'
_ssh_remote_server = 'ubuntu@{}'.format(_remote_server)
_nfs_remote_mp = '{}:/var/crash'.format(_remote_server)
_conffile = "/etc/default/kdump-tools"

#
# Used to indicate that netdump tests
# should not be run (SSH & NFS)
#
_local_only = False


class Phase(object):
    """The phase of the test to execute"""
    def __init__(self, phase):
        try:
            f = open('{}'.format(_next_phase), 'r')
            self.phase = f.read().strip()
            f.close()
        except FileNotFoundError:
            f = open('{}'.format(_next_phase), 'w')
            f.write("{}\n".format(phase))
            f.close()
            os.sync()
        finally:
            self.phase = phase

    def current(self):
        f = open('{}'.format(_next_phase), 'r')
        self.phase = f.read().strip()
        f.close()
        return self.phase

    def next(self, phase):
        f = open('{}'.format(_next_phase), 'w')
        f.write("{}\n".format(phase))
        f.close()
        os.sync()
        self.phase = phase
        return self.phase

    def kill(self):
        os.unlink('{}'.format(_next_phase))

    def set_conffile(self):
        with open("{}.ref".format(_conffile), "r") as orig:
            try:
                if self.phase == 'local' or self.phase == 'local-only':
                    with open("{}".format(_conffile), "w") as new_conf:
                        for line in orig.readlines():
                            if line.find('USE_KDUMP') == 0:
                                new_conf.write("{}".format('USE_KDUMP=1\n'))
                            else:
                                new_conf.write("{}".format(line))
                elif self.phase == 'ssh':
                    ref = orig.read()
                    orig.seek(0)
                    if ref.find("SSH") != -1:
                        with open("{}".format(_conffile), "w") as new_conf:
                            for line in orig.readlines():
                                if line.find('USE_KDUMP') == 0:
                                    new_conf.write(
                                        "{}".format('USE_KDUMP=1\n'))
                                else:
                                    new_conf.write("{}".format(line))
                            new_conf.write(
                                'SSH="{}"\n'.format(_ssh_remote_server))
                    else:
                        print("SSH functionality not found in {}".format(
                            '{}'.format(_conffile)))
                        return _EBAD
                elif self.phase == 'nfs':
                    ref = orig.read()
                    orig.seek(0)
                    if ref.find("NFS") != -1:
                        with open("{}".format(_conffile), "w") as new_conf:
                            for line in orig.readlines():
                                if line.find('USE_KDUMP') == 0:
                                    new_conf.write(
                                        "{}".format('USE_KDUMP=1\n'))
                                else:
                                    new_conf.write("{}".format(line))
                            new_conf.write('NFS="{}"\n'.format(_nfs_remote_mp))
                            #
                            # Adding HOSTTAG to test the functionality
                            # And avoid name collision b/w SSH and NFS
                            #
                            new_conf.write('HOSTTAG="hostname"\n')
                    else:
                        print("NFS functionality not found in {}".format(
                            '{}'.format(_conffile)))
                        return _EBAD
                else:
                    raise TypeError("Invalid test")
            except PermissionError as err:
                print(("User does not have the privilege "
                       "to change this file\t{}").format(err))
                return _EBAD
        return


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
        with open("{}.ref".format(_conffile), "r") as f:
            pass
    except FileNotFoundError:
        try:
            os.rename(
                "{}".format(_conffile), "{}.ref".format(_conffile))
        except PermissionError as err:
            print(("User does not have the privilege "
                   "to change this file\t{}").format(err))
            return _EBAD
    return


def run_test(test):
    if test == 'local':
        load = subprocess.Popen(["kdump-config", "load"])
        sleep(2)    # wait for the module to load
        action.next('ssh')
    elif test == 'ssh':
        action.next('nfs')
    elif test == 'nfs' or test == 'local-only':
        action.next('completed')
    else:
        raise TypeError("Invalid test")
    trigger_crash()
    return


def gather_test_results():
    if not _local_only:
        mount = subprocess.Popen(
            ["mount", "kdump-netcrash:/var/crash", "/mnt"])
        sleep(5)
    now = localtime(time())
    for path, dirs, files in os.walk(_crash_dir):
        if len(dirs) != 0 and dirs[0].find(str(now.tm_year)) == 0:
            os.rename(
                "{}/{}".format(path, dirs[0]),
                "{}/local_{}".format(path, dirs[0]))
    host = socket.gethostname()
    for path, dirs, files in os.walk('/mnt'):
        for dir in dirs:
            if dir.startswith(host):
                cp = subprocess.Popen(["cp", "-pr", "{}/{}".format(path, dir),
                                       "{}/nfs_{}".format(_crash_dir, dir)])
            else:
                cp = subprocess.Popen(["cp", "-pr", "{}/{}".format(path, dir),
                                       "{}/ssh_{}".format(_crash_dir, dir)])
    if not _local_only:
        sleep(2)
        mount = subprocess.Popen(["umount", "/mnt"])


if __name__ == '__main__':

    if len(sys.argv) > 1:
        crash_switch = True
        pass
    else:
        crash_switch = False

    if create_ref_conf() == _EBAD:
        exit(_EBAD)

    if _local_only:
        action = Phase('local-only')
    else:
        action = Phase('local')

    print("Running phase {}".format(action.current()))
    if action.phase != 'completed':
        if action.set_conffile() != _EBAD:
            run_test(action.phase)
        else:
            print("Unable to continue with tests")
            action.next('completed')
            exit(_EBAD)
    else:
        action.kill()
        gather_test_results()

# vim: et ts=4 sw=4
