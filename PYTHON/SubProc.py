import os
import subprocess
import sys
import StringIO

def StringIOExit(self):
    print "StringIOExit: %r" % self


if __name__ == '__main__':

    with file('subproc.out', 'w') as subproc_fp:
        status = subprocess.call(['ls', '-Flags'],
                                 stdout=subproc_fp,
                                 stderr=subproc_fp)
        print 'SUBPROC STATUS=%s' % status


#    output = subprocess.check_output(['ls', '-Flags'])
#    print "OUTPUT:\n%s" % output

    cmd = ["/nfs/software/PWE/tflex_nightly/LSF/bin/sbutil", "-h"]
    output = subprocess.check_output(cmd)
    print "OUTPUT:\n%r" % output
