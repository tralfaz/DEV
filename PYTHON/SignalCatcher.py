#!/gpfs/DEV/PLT/software/anaconda2-4.0.0/bin/python

import errno
import os
import signal
import sys
import time

class SignalHandler(object):

  def __init__(self):
    self._sigStack = []

  def handler(self, signum, frame):
    self._sigStack.append((signum, frame))
    print 'Handler signum=%s frame=%s' % (signum, frame)
 #   print 'FRAME: repr=%s dir=%r' % (repr(frame), dir(frame))
 #   print 'FRAME: f_back=%r' % frame.f_back
 #   print 'FRAME: f_builtins=%r' % frame.f_builtins
 #   print 'FRAME: f_code=%r' % frame.f_code
 #   print 'FRAME: f_exc_traceback=%r' % frame.f_exc_traceback
 #   print 'FRAME: f_exc_type=%r' % frame.f_exc_type
 #   print 'FRAME: f_exc_value=%r' % frame.f_exc_value
 #   print 'FRAME: f_globals=%r' % frame.f_globals
 #   print 'FRAME: f_lasti=%r' % frame.f_lasti
 #   print 'FRAME: f_lineno=%r' % frame.f_lineno
 #   print 'FRAME: f_locals=%r' % frame.f_locals
 #   print 'FRAME: f_restricted=%r' % frame.f_restricted
 #   print 'FRAME: f_trace=%r' % frame.f_trace

  def clearSignalStack(self):
    self._sigStack = []

  def peekSignalStack(self):
    if len(self._sigStack):
      return self._sigStack[-1]
    return None


if __name__ == '__main__':
  print sys.version
  print 'PID=%s' % os.getpid()

  sigHandler = SignalHandler()

  oldsig_handler = signal.getsignal(signal.SIGUSR1)
  print 'OLD SIGUSR1: %r' % oldsig_handler
  signal.signal(signal.SIGUSR1, sigHandler.handler)
#  signal.siginterrupt(signal.SIGUSR1, True)

  oldsig_handler = signal.getsignal(signal.SIGQUIT)
  print 'OLD SIGQUIT: %r' % oldsig_handler
  signal.signal(signal.SIGQUIT, sigHandler.handler)
  signal.siginterrupt(signal.SIGQUIT, True)

  oldsig_handler = signal.getsignal(signal.SIGHUP)
  print 'OLD SIGHUP: %r' % oldsig_handler
  signal.signal(signal.SIGHUP, sigHandler.handler)
  signal.siginterrupt(signal.SIGHUP, True)

  oldsig_handler = signal.getsignal(signal.SIGTERM)
  print 'OLD SIGTERM: %r' % oldsig_handler
  signal.signal(signal.SIGTERM, sigHandler.handler)
  signal.siginterrupt(signal.SIGTERM, True)

  while True:
    print 'Waiting...'
    try:
      time.sleep(10.0)
    except OSError as oserr:
      print 'OSError errno=%si msg=%s' % (oserr.errno, oserr.message)
    sigctx = sigHandler.peekSignalStack()
    if sigctx:
      print 'Sleep interrupted with signal %s' % sigctx[0]
      sigHandler.clearSignalStack()
    else:
      print 'Sleep timed out normally'
