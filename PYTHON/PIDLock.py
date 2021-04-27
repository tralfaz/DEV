import fcntl
import os
import sys


def write_pid(pidpath):
    pidFP = None
    try:
        pidFP = file(pidpath, 'a')
    except IOError as ioerr:
        return (None, 'OPEN')

    try:
        fcntl.flock(pidFP.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
    except IOError as ioerr:
        pidFP.close()
        return (None, 'LOCK')

    try:
        pidFP.seek(0)
        pidFP.truncate()
        pidFP.write('%s\n' % os.getpid())
        pidFP.flush()
    except IOError as ioerr:
        pidFP.close()
        return (None, 'WRITE')

    return (pidFP, '')

if __name__ == '__main__':
    pidFP = write_pid(sys.argv[1])
    raw_input('ENTER TO EXIT:')
