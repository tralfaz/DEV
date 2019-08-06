import curses
import sys


class App(object):

  def __init__(self):
    self._mainWin  = None
    self._stdscr   = None
    self._ttyCols  = -1
    self._ttyRows  = -1
    self._delegate = None
    self._inputProc   = None
    self._inputCtx    = None
    self._noInputProc   = None
    self._noInputCtx  = None
    self._quit     = False

  def appInit(self):
    # Init curses mode
    self._mainWin = curses.initscr()
    curses.noecho()  # turn off key echo
    curses.cbreak()  # turn of input buffering
    self._mainWin.keypad(1) # Process function key escape sequences as single key events
    curses.curs_set(0)
    if curses.has_colors():
      curses.start_color()
      curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
      curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
      curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
      curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
      curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
      curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
      curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
      curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLUE)
    
    self._ttyCols = curses.COLS
    self._ttyRows = curses.LINES

    curses.halfdelay(30)

    self._mainWin.clear()
    self._mainWin.refresh()
    
  def appFinish(self):
    # Restore starting terminal state
    self._mainWin.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

  def appQuit(self):
    curses.halfdelay(1)
    self._quit = True

  def main(self):
    curses.wrapper(self._wrapperMain)

  def mainLoop(self):
    while not self._quit:
      try:
        input = None
        input = self._mainWin.getkey()
      except curses.error as curx:
        if str(curx) == 'no input':
          if self._noInputProc:
            self._noInputProc(self, self._noInputCtx)
        else:
          raise curx
      if input and self._inputProc:
        self._inputProc(self, input, self._inputCtx)

  def mainWin(self):
    return self._mainWin

  def setDelegate(self, delegate):
    self._delegate = delegate

  def setInputCallback(self, callable, context):
    self._inputProc = callable
    self._inputCtx  = context

  def setNoInputCallback(self, callable, context):
    self._noInputProc = callable
    self._noInputCtx  = context

  def ttySize(self):
    return (self._ttyRows, self._ttyCols)

  def _wrapperMain(self, stdscr):
    self._stdscr = stdscr
    self.appInit()
    if self._delegate:
        self._delegate(self)
    else:
      self.mainLoop()
    self.appFinish()


class _TestDelegate(object):
  def __init__(self):
    self._app = None

  def initDelegate(self, app):
    self._app = app
    ttyRows, ttyCols = app.ttySize()

    label = "Curses App"
    app.mainWin().addstr( ttyRows//2, (ttyCols-len(label))//2, label) 
    label = "Press any key to exit"
    app.mainWin().addstr( ttyRows//2+2, (ttyCols-len(label))//2, label) 

    app.setInputCallback(self.inputCB, "CB ARG")
    
    app.mainLoop()

  def inputCB(self, app, input, ctx):
    app.appQuit()
    

if __name__ == "__main__":
  app = App()
  appDelegate = _TestDelegate()
  app.setDelegate(appDelegate.initDelegate)
  app.main()
