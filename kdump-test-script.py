#!/usr/bin/python3

test_phase = ['local', 'ssh', 'nfs']

def trigger_crash():
    try:
        f = open("/proc/sysrq-trigger","a")
        f.write('c')
    except PermissionError as err:
        print("Must be root to trigger a crash dump\t{}".format(err))

def run_test(test):
    f = open('/var/crash/next-test','w')
    if test == 'local':
        f.write('ssh\n')
        f.close()
    elif test == 'ssh':
        f.write('nfs\n')
        f.close()
    elif test == 'nfs':
        f.write('completed\n')
        f.close()
    else:
        raise TypeError("Invalid test")
    trigger_crash()
    return

if __name__ == '__main__':

    try:
        f = open('/var/crash/next-test','r')
        phase=f.read().strip()
    except FileNotFoundError:
        phase='local'
    print("Phase : {}".format(phase))
    if phase != 'completed':
        run_test(phase)

# vim: et ts=4 sw=4
