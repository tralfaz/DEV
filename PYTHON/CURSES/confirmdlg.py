import curses

import cursesapp
import dialog


__LOGFP = None #open("confirm.log", "w")

def LOG(msg):
  global __LOGFP
  if __LOGFP:
    __LOGFP.write(msg+"\n")
    __LOGFP.flush()

class ConfirmDialog(dialog.DialogWin):

  def __init__(self, parent, row, col, width, height):
    super(ConfirmDialog,self).__init__(parent, row, col, width, height)
    self._focus   = 0
    self._buttons = ["OK"]
    self._text = None

  def browseOptions(self):
    while True:
      try:
        key = None
        key = self.window().getkey()
      except curses.error as curx:
        if str(curx) != "no input":
          raise curx

      if key in ["KEY_RIGHT", "\t"]:
        self._focus = (self._focus+1) % len(self._buttons)
        self._drawButtons()
      elif key in ["KEY_LEFT", "KEY_BTAB"]:
        self._focus = max(self._focus-1,0)
        self._drawButtons()
      elif key in [" ", "\n"]:
        return (self._focus, self._buttons[self._focus])
      elif key == "\x1b":
        return None
                                 
  def setFocus(self, button):
    if type(button) is str and button in self._buttons:
      bdx = self._buttons.index(button)
    else:
      bdx = option
    if bdx < 0 or bdx > len(self._buttons)-1:
      return False
    self._focus = bdx
    self._drawButtons()
    return True

  def setButtons(self, buttons):
    self._buttons = buttons
    if self.visible():
      self.window().clear()
      self._drawButtonns()
      self._drawButtonns()

  def setText(self, text):
    self._text = text
    if self.visible():
      self.window().clear()
      self._drawText()
      self._drawButtons()
      
  def show(self):
    super(ConfirmDialog,self).show()
    self.window().keypad(1)
    self._drawText()
    self._drawButtons()
    
  def _drawButtons(self):
    if not self.visible():
      return
    dlgW, dlgH = self.size()
    win = self.window()
    sepr = dlgH-3
    win.addch(sepr, 0, curses.ACS_LTEE)
    for cdx in range(1, dlgW-1):
      win.addch(sepr, cdx, curses.ACS_HLINE)
    win.addch(sepr, dlgW-1, curses.ACS_RTEE)

    brow = dlgH - 2
    if len(self._buttons) == 1:
      btxt = "[" + self._buttons[0] + "]"
      bcol = (dlgW-len(btxt))//2
      attr = curses.A_REVERSE if self._focus == 0 else 0
      win.addstr(brow, bcol, btxt, attr)
    elif len(self._buttons) == 2:
      btxt1 = "[" + self._buttons[0] + "]"
      btxt2 = "[" + self._buttons[1] + "]"
      edge = (dlgW - (len(btxt1)+len(btxt2)+2)) // 3
      attr = curses.A_REVERSE if self._focus == 0 else 0
      win.addstr(brow, edge, btxt1, attr)
      attr = curses.A_REVERSE if self._focus == 1 else 0
      win.addstr(brow, dlgW-(len(btxt2)+edge+2), btxt2, attr)
    elif len(self._buttons) == 3:
      btxt1 = "[" + self._buttons[0] + "]"
      btxt2 = "[" + self._buttons[1] + "]"
      btxt3 = "[" + self._buttons[2] + "]"
      attr = curses.A_REVERSE if self._focus == 0 else 0
      win.addstr(brow, 2, btxt1, attr)
      attr = curses.A_REVERSE if self._focus == 1 else 0
      win.addstr(brow, (dlgW-len(btxt2))//2, btxt2, attr)
      attr = curses.A_REVERSE if self._focus == 2 else 0
      win.addstr(brow, dlgW-(len(btxt3)+2), btxt3, attr)

  def _drawText(self):
    if not self.visible() or not self._text:
      return
    lines = self._text.split('\n')
    dlgW, dlgH = self.size()
    win = self.window()
    txtR = ((dlgH-3)-len(lines)) // 2
    for ldx, line in enumerate(lines):
      line = line[:dlgW-2]
      txtC = (dlgW-(len(line))) // 2
      win.addstr(txtR+ldx, txtC, line)
                  


class TestDelegate(object):
  def __init__(self):
    self._app = None
    self._okdlg = None
    self._yndlg = None
    self._csadlg = None

  def initDelegate(self, app):
    self._app = app
    ttyRows, ttyCols = app.ttySize()
    app.setInputCallback(self.inputCB, "CB ARG")

    label = "Press 1, 2 or 3 for Dialog"
    app.mainWin().addstr( ttyRows//2, (ttyCols-len(label))//2, label) 
    label = "Press ESC to exit"
    app.mainWin().addstr( ttyRows//2+2, (ttyCols-len(label))//2, label) 

    app.mainLoop()

  def inputCB(self, app, input, ctx):
    ttyRows, ttyCols = app.ttySize()
    if input == "1":
      if not self._okdlg:
        width  = 30
        height = 10
        dlg = ConfirmDialog(app.mainWin(),
                            (ttyRows-height)//2, (ttyCols-width)//2,
                            width, height)
        dlg.setTitle("Operation Complete")
        dlg.setText("Drive Format Complete")
        self._okdlg = dlg        
      self._okdlg.show()
      choice = self._okdlg.browseOptions()
      msg = "You Selected: %r%s" % (choice, " " * ttyCols)
      app.mainWin().addstr(ttyRows-1, 1, msg[:ttyCols-2])
      self._okdlg.hide()
      
    elif input == "2":
      if not self._yndlg:
        width  = 30
        height = 10
        dlg = ConfirmDialog(app.mainWin(),
                            (ttyRows-height)//2, (ttyCols-width)//2,
                            width, height)
        dlg.setButtons(["NO", "YES"])
        dlg.setTitle("Confirm")
        dlg.setText("Can not undo.\nAre you sure?")
        self._yndlg = dlg        
      self._yndlg.setFocus("NO")
      self._yndlg.show()
      choice = self._yndlg.browseOptions()
      msg = "You Selected: %r%s" % (choice, " " * ttyCols)
      app.mainWin().addstr(ttyRows-1, 1, msg[:ttyCols-2])
      self._yndlg.hide()
      
    elif input == "3":
      if not self._csadlg:
        width  = 30
        height = 10
        dlg = ConfirmDialog(app.mainWin(),
                            (ttyRows-height)//2, (ttyCols-width)//2,
                            width, height)
        dlg.setButtons(["CANCEL", "SAVE", "APPLY"])
        dlg.setTitle("Settings Changes")
        dlg.setText("You have unsaved changes.\n"+
                    "What do want to do?")
        self._csadlg = dlg        
      self._csadlg.setFocus("SAVE")
      self._csadlg.show()
      while True:
        choice = self._csadlg.browseOptions()
        msg = "You Selected: %r%s" % (choice, " " * ttyCols)
        app.mainWin().addstr(ttyRows-1, 1, msg[:ttyCols-2])
        app.mainWin().refresh()
        if choice != (2, "APPLY"):
          break
      self._csadlg.hide()

    elif input == "\x1b":
      app.appQuit()
    

if __name__ == "__main__":
  app = cursesapp.App()
  appDelegate = TestDelegate()
  app.setDelegate(appDelegate.initDelegate)
  app.main()
