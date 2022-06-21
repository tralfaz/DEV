import json
import os
import pwd
import socket
import subprocess
import sys
import time

def exec_command_as(asuser, cmd):
    readFD, writeFD = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(readFD)
        pwent = pwd.getpwnam(asuser)
        os.setgid(pwent.pw_gid)
        os.setuid(pwent.pw_uid)

        cmdargs = cmd.split()
        cmdout = subprocess.check_output(cmdargs)
        print "EXECC AS(%s): %s"  % (asuser, cmdout)
        os.write(writeFD, cmdout)
        os.close(writeFD)
        sys.exit(0)

    else:
        os.close(writeFD)
        print 'EXECP: EUID=%s UID=%s  EGID=%s GID=%s' % \
            (os.geteuid(),os.getuid(),os.getegid(),os.getgid())

        execout = ''
        eof = False
        while not eof:
            buf = os.read(readFD, 64*1024)
            print "BUF: %r" % buf
            if buf:
                execout += buf
            else:
                eof = True
        os.close(readFD)
        print "EXECPOUT: %r" % execout
        return execout
        
        
def child_responder(msgSKT):
    print "CHILD: EUID=%s UID=%s EGID=%s GID=%s" % \
          (os.geteuid(), os.getuid(),os.getegid(), os.getgid())

    while True:
        msgjson = msgSKT.recv(16*1024)
        if not msgjson:
            break
        
        msgobj = json.loads(msgjson)
        requser = msgobj.get('user')
        reqcmd  = msgobj.get('cmd')
        print 'CHILD: user=%s cmd=%s' % (requser, reqcmd)
        output = exec_command_as(requser, reqcmd)
        msgSKT.send(output)


def parent_requester(msgSKT):
    while True:
        requser = raw_input('user: ')
        if not requser:
            continue
        reqcmd = raw_input('command: ')
        reqjson =  json.dumps({ 'user':requser, 'cmd':reqcmd })
        msgSKT.send(reqjson)
        result = msgSKT.recv(64*1024)
        print 'PARENT: result=%s' % result
    


if __name__ == '__main__':
    
    safe_userent = None
    if len(sys.argv) > 1:
        safe_userent = pwd.getpwnam(sys.argv[1])
        parentSKT, childSKT = sockPair = socket.socketpair()
        print "PAIR: P:%s C:%s" % (parentSKT, childSKT)

    print 'EUID=%s UID=%s  EGID=%s GID=%s' % \
          (os.geteuid(),os.getuid(),os.getegid(),os.getgid())

    print subprocess.check_output(['/usr/bin/id'])

    if os.getuid() == 0:
        childPid = os.fork()
        if childPid < 0:
            print 'ERROR: fork failed'
            sys.exit(1)
        
        if childPid == 0:
          # child process
          child_responder(childSKT)

        # parent thread
        if safe_userent:
            os.setgid(safe_userent.pw_gid)
            os.setuid(safe_userent.pw_uid)
        print 'PARENT: EUID=%s UID=%s  EGID=%s GID=%s' % \
              (os.geteuid(),os.getuid(),os.getegid(),os.getgid())
        parent_requester(parentSKT)
