import curses

import cursesapp
import dialog


__LOGFP = None #open("optiondlg.log", "w")
def LOG(msg):
  global __LOGFP
  if __LOGFP:
    __LOGFP.write(msg+"\n")
    __LOGFP.flush()

class OptionDialog(dialog.DialogWin):

  def __init__(self, parent, row, col, width, height):
    super(OptionDialog,self).__init__(parent, row, col, width, height)
    self._options = []
    self._selection = None

  def browseOptions(self):
    while True:
      try:
        key = None
        key = self.window().getkey()
      except curses.error as curx:
        if str(curx) != "no input":
          raise curx

      if key == "KEY_DOWN" and self._selection is not None:
        self._selection = min(self._selection+1, len(self._options)-1)
        LOG("KEY_DOWN %s" % self._selection)
        self._drawOptions()
      elif key == "KEY_UP" and self._selection is not None:
        self._selection = max(self._selection-1, 0)
        self._drawOptions()
        LOG("KEY_UP %s" % self._selection)
      elif key == "\n":
        return (self._selection, self._options[self._selection])
      elif key == "\x1b":
        return None
                                 
  def selectOption(self, option):
    if type(option) is str and option in self._options:
      odx = self._options.index(option)
    else:
      odx = option
    if odx < 0 or odx > len(self._options)-1:
      return False
    self._selection = odx
    self._drawOptions()
    return True

  def setOptions(self, options):
    self._options = options
    self._drawOptions()

  def show(self):
    super(OptionDialog,self).show()
    self.window().keypad(1)
    self._drawOptions()
    
  def _drawOptions(self):
    if not self.visible():
        return
    optW = self.size()[0] - 2
    pad = " " * optW
    for odx, option in enumerate(self._options):
      otxt = (option + pad)[:optW]
      attr = curses.A_REVERSE if odx == self._selection else 0
      self.window().addstr(odx+1, 1, otxt, attr)
    self.refresh()



class TestDelegate(object):
  def __init__(self):
    self._app = None

  def initDelegate(self, app):
    self._app = app
    ttyRows, ttyCols = app.ttySize()
    app.setInputCallback(self.inputCB, "CB ARG")


    label = "Press 1 for Option Dialog"
    app.mainWin().addstr( ttyRows//2, (ttyCols-len(label))//2, label) 
    label = "Press ESC to exit"
    app.mainWin().addstr( ttyRows//2+2, (ttyCols-len(label))//2, label) 

    app.mainLoop()

  def inputCB(self, app, input, ctx):
    ttyRows, ttyCols = app.ttySize()
    if input == "1":
      width  = 30
      height = 10
      self._optdlg = OptionDialog(app.mainWin(),
                                  (ttyRows-height)//2, (ttyCols-width)//2,
                                  width, height)
      self._optdlg.setTitle("Choose One")
      self._optdlg.setOptions(["Option One", "Second Thing",
                               "This is a very long option that should not fit"])
      self._optdlg.selectOption(0)
      self._optdlg.show()
      choice = self._optdlg.browseOptions()
      msg = "You Selected: %r%s" % (choice, " " * ttyCols)
      app.mainWin().addstr(ttyRows-1, 1, msg[:ttyCols-2])
      self._optdlg.hide()
      
    elif input == "\x1b":
      app.appQuit()
    

if __name__ == "__main__":
  app = cursesapp.App()
  appDelegate = TestDelegate()
  app.setDelegate(appDelegate.initDelegate)
  app.main()
