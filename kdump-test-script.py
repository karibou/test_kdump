#!/usr/bin/python3
import os
import sys
import subprocess
import time
import platform
import apt
import apt.progress

_EBAD = -1
_crash_dir = '/var/crash'
_next_phase = '{}/next-test'.format(_crash_dir)
_remote_server = 'kdump-netcrash'
_ssh_remote_server = 'ubuntu@{}'.format(_remote_server)
_nfs_remote_mp = '{}:/var/crash'.format(_remote_server)
_conffile = "/etc/default/kdump-tools"
_defaults_file = "/etc/default/kdump-test-script"



def get_defaults():
    try:
        with open("{}".format(_defaults_file, 'r')) as defaults:
            for env_var in defaults.readlines():
                var = env_var.partition('=')[0]
                val = "{}".format(env_var.partition('=')[len(env_var.partition('='))-1]).strip()
                if not var.startswith("#") and val != '0':
                    os.environ.setdefault('{}'.format(var), '{}'.format(val))
    except FileNotFoundError:
            pass
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
                "{}".format(_conffile),
                "{}.ref".format(_conffile))
        except PermissionError as err:
            print(("User does not have the privilege "
                   "to change this file\t{}").format(err))
            return _EBAD
        except FileNotFoundError:
            print("Unable to find {}".format(_conffile))
            return _EBAD
    return


def run_test(test):
    if test == 'local':
        try:
            load = subprocess.check_output(["kdump-config", "load"])
        except subprocess.CalledProcessError:
            print("Unable to load kdump module")
            return _EBAD
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
        try:
            subprocess.check_output(
                ["mount", "kdump-netcrash:/var/crash", "/mnt"])
        except subprocess.CalledProcessError:
            print("Unable to mount remote server to collect results")
            return _EBAD
    now = time.localtime(time.time())
    for path, dirs, files in os.walk(_crash_dir):
        if dirs and dirs[0].find(str(now.tm_year)) == 0:
            os.rename(
                "{}/{}".format(path, dirs[0]),
                "{}/local_{}".format(path, dirs[0]))
    if not _local_only:
        host = platform.node()
        for path, dirs, files in os.walk('/mnt'):
            for dir in dirs:
                try:
                    if dir.startswith(host):
                        cp = subprocess.check_output([
                            "cp", "-pr", "{}/{}".format(path, dir),
                            "{}/nfs_{}".format(_crash_dir, dir)])
                    else:
                        cp = subprocess.check_output([
                            "cp", "-pr", "{}/{}".format(path, dir),
                            "{}/ssh_{}".format(_crash_dir, dir)])
                except subprocess.CalledProcessError:
                    print("Unable to copy files from remote server")
                    return _EBAD

    if not _local_only:
        try:
            mount = subprocess.check_output(["umount", "/mnt"])
        except subprocess.CalledProcessError:
            print("Unable to unmount /mnt")
            return _EBAD

def crash_check(kernel, core):
    print("running crash -st {} {}".format(kernel, core))
    try:
        subprocess.check_output(["crash", "-st", kernel, core], stderr=subprocess.DEVNULL)
        return
    except subprocess.CalledProcessError as crash_error :
        print("crash test failed for {}".format(core))
        print("Error Output\n{}".format(crash_error.output.decode("UTF-8")))
        return _EBAD

def analyse_results():
    if _no_result:
        print("Result Analysis overriden by NO_RESULT")
        return
    else:
        print("Running result analysis")
        #
        # First we get the dbgsym package
        #
        with open("/etc/apt/sources.list.d/ddebs.list", "w") as ddebs:
            try:
                release= platform.dist()[2]
                for archive in '', '-security', '-updates', '-proposed':
                    ddebs.write(("deb http://ddebs.ubuntu.com/ {}{:10}"
                    "main restricted universe multiverse\n".format(release, archive)))
                ddebs.close()
            except:
                print("Unable to create /etc/apt/sources.list.d/ddebs.list")
                return _EBAD
        print("Updating APT cache with new sources")
        cache=apt.Cache()
        kern_vers = platform.release()
        cache.update()
        cache.open()
        pkg = cache['linux-image-{}-dbgsym'.format(kern_vers)]
        if not pkg.is_installed:
            try:
                pkg.mark_install()
                print("Installing linux-image-{}-dbgsym".format(kern_vers))
                cache.commit()
            except KeyError:
                print("Unable to find linux-image-{}-dbgsym".format(kern_vers))
                return _EBAD

        namelist = '/usr/lib/debug/boot/vmlinux-{}'.format(kern_vers)

        for path, dirs, files in os.walk(_crash_dir):
            if not dirs:
                dumpfile = [dumpfile for dumpfile in files if 'dump' in dumpfile][0]
                error = crash_check(namelist, '{}/{}'.format(path, dumpfile))
        return error

if __name__ == '__main__':
    # First get the environment variable
    # if they are defined in /etc/default/test-kdump-script
    #
    get_defaults()

    # If not, they can still be defined in the environment.
    # Define LOCAL_ONLY = 1 as an environment variable
    # to indicate that netdump tests should not be run (SSH & NFS)
    #
    # NO_RESULT = 1 will override the analysis of the results
    # which can be time consuming
    _local_only = bool(os.environ.get('LOCAL_ONLY', False))
    _no_result = bool(os.environ.get('NO_RESULT', False))

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
            sys.exit(_EBAD)
    else:
        action.kill()
        ret = gather_test_results()
        if not ret:
            ret = analyse_results()
        else:
            sys.exit(ret)

# vim: et ts=4 sw=4
