import curses

__LOGFP = None #file("msgwin.log", "w")
def LOG(msg):
  global __LOGFP
  if __LOGFP:
    __LOGFP.write(msg+"\n")
    __LOGFP.flush()

class MessageWin(object):

  def __init__(self, parent, row, col, width, height):
    self._parent = parent
    self._row    = row
    self._col    = col
    self._width  = width
    self._height = height
    self._msgWin = None
    self._title  = (None, 0, 2)
    self._lines  = []
    self._scroll = 0
    self._shift  = 0
    self._shown  = False
    
  def add(self, msg, jump=False):
    self._lines.append(msg)
    if not self.visible():
      return
    if jump:
      self._scroll = self._shift = 0
    if len(self._lines) > self._height-2:
      self._msgWin.clear()
      self._drawFrame()
      self._drawLines()
    else:
      addRow = min(len(self._lines), self._height-2)
      self._msgWin.addstr(addRow, 1, msg[self._shift:self._shift+self._width-2])
    self._msgWin.refresh()
    
  def browse(self):
    if not self.visible():
      return
    input = ""
    while input != "\x1b":
      input = self.read()
      if input == "KEY_UP":
        self.scroll(1)
      elif input == "KEY_DOWN":
        self.scroll(-1)
      elif input == "KEY_LEFT":
        self.shift(1)
      elif input == "KEY_RIGHT":
        self.shift(-1)
      elif input == "KEY_PPAGE":
        self.scroll(self._height-2)
      elif input == "KEY_NPAGE":
        self.scroll(-(self._height-2))
      elif input == "KEY_HOME":
        self.home()
      elif input == "KEY_END":
        self.end()
    self.hide()

  def clear(self):
    self._lines = []
    self._scroll = 0
    if self.visible():
      self._msgWin.clear()
      self._msgWin.refresh()

  def count(self):
    return len(self._lines)
  
  def end(self):
    self._shift = 0
    self._scroll = 0
    self.scroll(0)

  def hide(self):
    if not self.visible():
      return
    del self._msgWin
    self._msgWin = None
    self._parent.touchwin()
    self._parent.refresh()
    self._shown = False

  def home(self):
    self._shift = 0
    self.scroll(len(self._lines))

  def read(self):
    if self.visible():
      while True:
        try:
          return self._msgWin.getkey()
        except curses.error as curx:
          if str(curx) == 'no input':
            continue
          else:
            raise curx
    return None
      
  def scroll(self, delta):
    self._scroll += delta
    self._scroll = max(self._scroll, 0)
    self._scroll = min(self._scroll, len(self._lines)-(self._height-2))
    if self.visible():
      self._msgWin.clear()
      self._drawFrame()
      self._drawLines()
      self._msgWin.refresh()
        
  def shift(self, delta):
    maxShift = max([len(s) for s in self._lines]) - (self._width-2)
    self._shift = min(max(0,self._shift+delta), maxShift)
    self.scroll(0)

  def setTitle(self, title, row=0, col=2):
    self._title = (title, row, col)

  def show(self):
    if self.visible():
      return
    self._msgWin = curses.newwin(self._height, self._width, self._row, self._col)
    self._msgWin.keypad(True)
    self._drawFrame()
    self._drawLines()
    self._msgWin.refresh()
    self._shown = True

  def visible(self):
    return self._shown

  def _drawFrame(self):
    self._msgWin.box()
    if self._title[0]:
      self._msgWin.addstr(self._title[1], self._title[2], self._title[0])

  def _drawLines(self):
    if self._lines:
      start = max(len(self._lines)-(self._height-2)-self._scroll, 0)
      end   = start + self._height - 2
      shift = self._shift
      for y, line in enumerate(self._lines[start:end]):
        self._msgWin.addstr(y+1, 1, line[shift:shift+self._width-2])

        

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

  msgWin = MessageWin(mainWin, 4, 4, 70, 20)
  msgWin.setTitle("Messages:")
  msgNum = 1
  msgLen = 10

  
  while input != ESC:
    try:
      input = mainWin.getkey()
    except curses.error as curx:
      if str(curx) == 'no input':
        input = "<NoInput>"
      else:
        raise curx

    if input.lower() == 'a':
      msg = "MSG(%02d) %s" % (msgNum, chr(ord('A')+msgNum-1)*msgLen)
      msgWin.add(msg, input == 'A')
      msgNum += 1
      msgLen += 10
    elif input == 'b':
      msgWin.browse()
    elif input == 'h':
      msgWin.hide()
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
