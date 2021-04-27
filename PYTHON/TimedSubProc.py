import os
import shlex
import subprocess
import sys
import threading
import time

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def run(cmd, timeout_sec):
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE)
  kill_proc = lambda p: p.kill()
  timer = threading.Timer(timeout_sec, kill_proc, [proc])
  try:
    timer.start()
    stdout,stderr = proc.communicate()
  finally:
    timer.cancel()


def run_inspector(script, node,  timeout):
    inspthr = NodeInspector(script, node, timeout)
    inspthr.start()
    inspthr.join()
    return inspthr.results()


class NodeInspector(threading.Thread):
    """Node InspectorCPU """

    def __init__(self, script, node, timeout=None, attempt=1):
        """A runnable context to execute a shell script that will exedute a
        ssh/rsh request to a specified node, and limit the response time with
        specified timeout
        Arguments:
          script, Full path to script to execute with time limit
          node, Host name that script will ssh/rsh execution to
          timeout, Seconds, as float, to limit script completion time
        """
        super(NodeInspector,self).__init__(name='NodeInspector')

        self._script   = script
        self._node     = node
        if timeout:
            self._timer = threading.Timer(timeout, self._timeout_cb)
        else:
            self._timer = None
        self._attempt   = attempt
        
        self._subproc  = None
        self._timedout = False
        self._stdout   = None
        self._stderr   = None
#        self.daemon    = True

    def killproc(self):
        if not self.is_alive():
            return

        subsid = os.getsid(self._subproc.pid)
        killcmd = ['/usr/bin/pkill', '-9', '-s', '%s' % subsid]
        killproc = subprocess.Popen(killcmd, shell=False, close_fds=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        stdout, stderr = killproc.communicate()

    def results(self):
      """Returns a disctionary of the results of the node inspection, including
      the following information, node, ssh status, ssh stdout, ssh stderr,
      timedout flag, attempt number."""
      return { 'node':self._node, 'status': self._subproc.returncode,
               'stdout':self._stdout, 'stderr':self._stderr,
               'timedout':self._timedout, 'attempt': self._attempt }
            
    def run(self):
        """Execute the specified script in a suprocess collecting the stdout
        and stderr.  If a timeout was specified force exit the script
        completing the thread run."""
        try:
#            print "Thread(%s) starts..." % self._node
#            print "Thread(%s) PID=%s PGRP=%s" % (self._node, os.getpid(), os.getpgrp())
            # Run script in a unique session ID to enable process tree kill
            cmd = ['/usr/bin/setsid', self._script, self._node]
            self._subproc = subprocess.Popen(cmd, shell=False, close_fds=True,
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE)
            if self._timer:
                self._timer.start()

            subsid = os.getsid(self._subproc.pid)
#            print "SubProc(%s) PID=%s PGRP=%s SID=%s" % (self._node, self._subproc.pid, os.getpgid(self._subproc.pid), subsid) 
            self._stdout,self_stderr = self._subproc.communicate()
#            print "InspectOUT(%s): %r" % (self._node, self._stdout)
#            print "InspectERR(%s): %r" % (self._node, self._stderr)
#            print "Thread(%s) normal end." % self._node

        except Exception as exc:
            print "Thread(%s) Exception %r %s", (self._node, exc, exc)
            return "ERROR"
        finally:
            if self._timer:
                self._timer.cancel()

    def _timeout_cb(self):
        """Thread timer calback that if invoke kills the scripts sub-process
        tree via pkill and session id."""
#        print "\nThread(%s)._timeout_cb" % self._node
        self._timedout = True
        self.killproc()

def inspector():
    script = '/home/mmarchio/DEV/PYTHON/InspectNode.sh'
    thrpool = ProcessPoolExecutor(max_workers=5)
    print "START: %s" % time.time()
    for nodenum in xrange(100,200):
        node = "fnode%d" % nodenum
        future = thrpool.submit(run_inspector, script, node, 10.0)
        print "Submitted: %s" % node
        future.add_done_callback(inspect_done_cb)
        
    thrpool.shutdown()
    print "END: %s" % time.time()


def inspect_done_cb(future):
    print "Inspect Done: %r" % future.result()

#
# MAIN
#
if __name__ == '__main__':
    insthr = threading.Thread(name="Inspector", target=inspector)
    insthr.daemon = True
    insthr.start()

    raw_input("FOO")
    print "\nEND MAIN"
