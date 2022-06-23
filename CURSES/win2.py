import curses
import curses.wrapper

class WinBorder:
  def __init__(self):
    self.left  = 0
    self.right = 0
    self.top   = 0
    self.bot   = 0
    self.topl  = 0
    self.topr  = 0
    self.botl  = 0
    self.botr  = 0

  def dashPlus(self):
    self.left  = self.right = '|'
    self.top   = self.bot   = '-'
    self.topl  = self.topr  = '+'
    self.botl  = self.botr  = '+'

class Frame:
  def __init__(self, win, row, col, height, width):
    self.win = win
    self.row = row
    self.col = col
    self.height = height
    self.width  = width
    self.border = WinBorder()
    self.border.dashPlus()
    
  def centerOnScreen(self):
    self.row = (curses.LINES - self.height) // 2
    self.col = (curses.COLS  - self.width)  // 2

  def drawBox(self):
    self.win.move(self.row, self.col)
    self.win.addch(self.border.topl)
    self.win.move(self.row, self.col+self.width)
    self.win.addch(self.border.topr)
    self.win.move(self.row+self.height, self.col)
    self.win.addch(self.border.botl)
    self.win.move(self.row+self.height, self.col+self.width)
    self.win.addch(self.border.botr)
    self.win.move(self.row, self.col+1)
    self.win.hline(self.border.top, self.width-1)
    self.win.move(self.row+self.height, self.col+1)
    self.win.hline(self.border.bot, self.width-1)
    self.win.move(self.row+1, self.col)
    self.win.vline(self.border.left, self.height-1)
    self.win.move(self.row+1, self.col+self.width)
    self.win.vline(self.border.left, self.height-1)
    self.win.refresh()
    
  def eraseBox(self):
    for row in xrange(self.row,self.row+self.height+1):
      for col in xrange(self.col,self.col+self.width+1):
        self.win.move(row, col)
        self.win.addch(' ')
    self.win.refresh()

        
def main(stdscr=None, *args):
  if not stdscr:
    stdscr = curses.initscr()

  curses.start_color()
  curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
  curses.noecho() # turn off key echo
  curses.cbreak() # turn of input buffering
  stdscr.keypad(1) # Process function key escape sequences as single key events

  frame = Frame(stdscr, 0, 0, 3, 10)
  frame.centerOnScreen()

  stdscr.attron(curses.color_pair(1))
  stdscr.addstr("Press F1 to exit")
  stdscr.refresh()
  stdscr.attroff(curses.color_pair(1))

  frame.drawBox()
  while True:
    key = stdscr.getch()
    if key == curses.KEY_LEFT:
      frame.eraseBox()
      frame.col -= 1
      frame.drawBox()
    elif key == curses.KEY_RIGHT:
      frame.eraseBox()
      frame.col += 1
      frame.drawBox()
    elif key == curses.KEY_UP:
      frame.eraseBox()
      frame.row -= 1
      frame.drawBox()
    elif key == curses.KEY_DOWN:
      frame.eraseBox()
      frame.row += 1
      frame.drawBox()
    elif key == curses.KEY_F1:
      break

  # Restore starting terminal state
  stdscr.keypad(0)
  curses.nocbreak()
  curses.echo()

  curses.endwin()


curses.wrapper(main)
