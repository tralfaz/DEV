import curses

__LOGFP = file("dialog.log", "w")
def LOG(msg):
  global __LOGFP
  if __LOGFP:
    __LOGFP.write(msg+"\n")
    __LOGFP.flush()

class DialogWin(object):

  class Label:

    def __init__(self, text, row, col,  attr=None):
      self.text = text
      self.row  = row
      self.col  = col
      self.attr = attr
      
  def __init__(self, parent, row, col, width, height):
    self._parent  = parent
    self._row     = row
    self._col     = col
    self._width   = width
    self._height  = height
    self._window  = None
    self._title   = (None, 0, 2)
    self._shown   = False
    self._labels  = []
    self._symbols = []
    self._separators = []
    
  def addHSep(self, row, col, length, attr=0):
    text = "-" * length
    if row < 0 or row > self._height-1:
      return None
    if col + len(text) < 0:
       return None
    if col < 0:
      text = text[-col:]
      col = 0
    if col + len(text) > self._width:
      text = text[0:(self._width)-(col+len(text))]
    sep = DialogWin.Label(text, row, col, attr)
    self._separators.append(sep)
    if not self.visible():
      return sep
    for x,c in enumerate(text):
      self._win.addch(row, col+x, curses.ACS_HLINE, attr)
    self._win.refresh()
    return sep
    
  def addLabel(self, text, row, col, attr=0):
    if row < 0 or row > self._height-1:
      return None
    if col + len(text) < 0:
       return None
    if col < 0:
      text = text[-col:]
      col = 0
    if col + len(text) > self._width:
      text = text[0:(self._width)-(col+len(text))]
    lbl = DialogWin.Label(text, row, col, attr)
    self._labels.append(lbl)
    if not self.visible():
      return lbl
    self._win.addstr(row, col, text, attr)
    self._win.refresh()
    return lbl
  
  def addSymbol(self, symbol, row, col, attr=0):
    if row < 0 or row > self._height-1:
      return None
    if col < 0 or col > self._width-1:
       return None
    sym = DialogWin.Label(symbol, row, col, attr)
    self._symbols.append(sym)
    if not self.visible():
      return sym
    self._win.addch(row, col, text, attr)
    self._win.refresh()
    return sym
  
  def addVSep(self, row, col, length, attr=0):
    text = "|" * length
    if col < 0 or col > self._width-1:
      return None
    if row + len(text) < 0:
       return None
    if row < 0:
      text = text[-row:]
      row = 0
    if row + len(text) > self._height:
      text = text[0:(self._height)-(row+len(text))]
    sep = DialogWin.Label(text, row, col, attr)
    self._separators.append(sep)
    if not self.visible():
      return sep
    for x,c in enumerate(text):
      self._win.addch(row+x, col, curses.ACS_VLINE, attr)
    self._win.refresh()
    return sep
    
  def hide(self):
    if not self.visible():
      return
    del self._win
    self._win = None
    self._parent.touchwin()
    self._parent.refresh()
    self._shown = False

  def setTitle(self, title, row=0, col=2):
    self._title = (title, row, col)

  def read(self):
    if self.visible():
      while True:
        try:
          return self._win.getkey()
        except curses.error as curx:
          if curx.message == 'no input':
            continue
          else:
            raise curx
    return None
      
  def show(self):
    if self.visible():
      return
    self._win = curses.newwin(self._height, self._width, self._row, self._col)
    self._win.keypad(True)
    self._drawFrame()
    for lbl in self._labels:
      self._win.addstr(lbl.row, lbl.col, lbl.text, lbl.attr)
    for sym in self._symbols:
      self._win.addch(sym.row, sym.col, sym.text, sym.attr)
    for sep in self._separators:
      if sep.text[0] == "-":
        for x,c in enumerate(sep.text):
          self._win.addch(sep.row, sep.col+x, curses.ACS_HLINE, sep.attr)
      elif sep.text[0] == "|":
        for x,c in enumerate(sep.text):
          self._win.addch(sep.row+x, sep.col, curses.ACS_VLINE, sep.attr)
    self._win.refresh()
    self._shown = True

  def visible(self):
    return self._shown

  def _drawFrame(self):
    self._win.box()
    if self._title[0]:
      self._win.addstr(self._title[1], self._title[2], self._title[0])

def main(stdscr):

  # Init curses mode
  mainWin = curses.initscr()
  curses.noecho()  # turn off key echo
  curses.cbreak()  # turn of input buffering
  mainWin.keypad(1) # Process function key escape sequences as single key events
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
    
  ttyCols = curses.COLS
  ttyRows = curses.LINES

  mainWin.clear()

  for row in range(ttyRows):
    line = chr(ord('A')+row) * ttyCols
    mainWin.addstr(row, 0, line[:-1])

  mainWin.refresh()

  ESC = "\x1b"
  curses.halfdelay(30)
  input = ""

  dlg1 = DialogWin(mainWin, 4, 4, 70, 20)
  dlg1.setTitle("Dialog One:")
  dlg1.addLabel("Label One", 10, 30, curses.color_pair(3)|curses.A_BLINK)
  dlg1.addLabel("Reverse", 11, 30, curses.color_pair(1)|curses.A_REVERSE)
  dlg1.addLabel("Underline", 12, 30, curses.color_pair(1)|curses.A_UNDERLINE)
  dlg1.addLabel("0123456789 Left Clipped", 4, -5)
  dlg1.addLabel("Right Clipped 0123456789", 4, 50)
  dlg1.addSymbol(curses.ACS_PLMINUS, 10, 28, curses.A_BOLD)
  dlg1.addHSep(15, 20, 20, curses.color_pair(2)|curses.A_BOLD)
  dlg1.addVSep(5, 5, 8, curses.color_pair(2)|curses.A_BOLD)
  
  while input != ESC:
    try:
      input = mainWin.getkey()
    except curses.error as curx:
      if curx.message == 'no input':
        input = "<NoInput>"
      else:
        raise curx

    if input == "KEY_UP":
      msgWin.scroll(1)
    elif input == "KEY_DOWN":
      msgWin.scroll(-1)
    elif input == "KEY_PPAGE":
      msgWin.scroll(18)
    elif input == "KEY_NPAGE":
      msgWin.scroll(-18)
    elif input == '1':
      dlg1.show()
      input = dlg1.read()
      dlg1.hide()
      mainWin.addstr(ttyRows-1,0, input, curses.color_pair(5)|curses.A_BOLD)
      
    elif input == 'h':
      msgWin.hide()
      ms
    elif input == 's':
      msgWin.show()
    else:
      mainWin.addstr(0,0, input, curses.color_pair(7)|curses.A_BOLD)

  # Restore starting terminal state
  mainWin.keypad(0)
  curses.nocbreak()
  curses.echo()
  curses.endwin()

  
if __name__ == '__main__':
  curses.wrapper(main)
