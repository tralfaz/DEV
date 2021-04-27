import os
import Queue
import shlex
import subprocess
import sys
import threading
import time

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from shared.config import TRAMConfig
from shared.config.configutils import hosts_arg_to_host_set



def _run_node_discovery(script, node,  timeout):
    inspthr = NodeInspector(script, node, timeout)
    inspthr.start()
    inspthr.join()
    return inspthr.results()


class NodeCollector(threading.Thread):
    """A Daemon thread that accepts queued colletor requests to inpect
    undiscovered nodes, start CRMS agents on newly added nodes, and schedule
    CRMS agent shutdowns on removed nodes."""
    def __init__(self, script, node, timeout=None, attempt=1):
        """A runnable context to execute a shell script that will exedute a
        ssh/rsh request to a specified node, and limit the response time with
        specified timeout
        Arguments:
          script, Full path to script to execute with time limit
          node, Host name that script will ssh/rsh execution to
          timeout, Seconds, as float, to limit script completion time
        """
        super(NodeCollector,self).__init__(name='NodeCollector')
        self.daemon = True

        self._cmdqueue = Queue.Queue()

        self._execpool = ProcessPoolExecutor(max_workers=5)

        tramcfg = TRAMConfig.instance()
        instpath = tramcfg.system_param('tram_install_dir')
        self._discscript = os.path.join(instpath, 'etc', 'tram.sh')

    def discover_nodes(self, hosts):
        hostset = hosts_arg_to_host_set(hosts)
        for host in hostset:
            self._execpool.submit(_run_node_discover, self._discscript,
                                  host, 10.0)

    def shutdown_nodes(self, hosts):
        hostset = hosts_arg_to_host_set(hosts)

    def startup_nodes(self, hosts):
        hostset = hosts_arg_to_host_set(hosts)


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
    """Timed subpocess operation to disover the hardware resources of a
    specific node within a CRMS cluster.  The inspector attempts to gather
    the number of CPU socket, cores, and thread, plus te memory size in GBs.
    """

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
        self.daemon    = True

    def killproc(self):
        """Abort the inspection subprocess via the pkill command to stop the
        entire process tree of the node inspection sub-process."""
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
            # Run script in a unique session ID to enable process tree kill
            cmd = ['/usr/bin/setsid', self._script, self._node]
            self._subproc = subprocess.Popen(cmd, shell=False, close_fds=True,
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE)
            if self._timer:
                self._timer.start()

            subsid = os.getsid(self._subproc.pid)
            self._stdout,self_stderr = self._subproc.communicate()

        except Exception as exc:
            print "Thread(%s) Exception %r %s", (self._node, exc, exc)
            return "ERROR"
        finally:
            if self._timer:
                self._timer.cancel()

    def _timeout_cb(self):
        """Thread timer calback that if invoke kills the scripts sub-process
        tree via pkill and session id."""
        self._timedout = True
        self.killproc()



def inspect_done_cb(future):
    print "Inspect Done: %r" % future.result()

#
# MAIN
#
if __name__ == '__main__':

    script = '/home/mmarchio/DEV/PYTHON/InspectNode.sh'

    ncoll = NodeCollector

    print "START: %s" % time.time()
    for nodenum in xrange(100,200):
        node = "fnode%d" % nodenum
        future = thrpool.submit(run_inspector, script, node, 10.0)
        print "Submitted: %s" % node
        future.add_done_callback(inspect_done_cb)
        
    thrpool.shutdown()
    print "END: %s" % time.time()


    insthr = threading.Thread(name="Inspector", target=inspector)
    insthr.daemon = True
    insthr.start()

    raw_input("FOO")
    print "\nEND MAIN"
