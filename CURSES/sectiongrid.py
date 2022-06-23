import curses
import curses.wrapper
import getpass
import os
import logging
import subprocess
import sys

LOG = logging.getLogger('sbmonitor')


def CenterLine(win, line):
  maxRows, maxCols = win.getmaxyx()
  row = maxRows // 2
  col = (maxCols - len(line)) // 2
  win.move(row, col)
  win.addstr(line)


class SectionInfo(object):

  def __init__(self):
    self._aid   = -1
    self._icons = ['-', '-']
    self._colors = [0, 0]
  

class SectionGrid(object):

  def __init__(self, sectionRows, sectionCols):
    self._sectionRows = sectionRows
    self._sectionCols = sectionCols
    self._stateIcons  = None
    LOG.debug("SECDIM: %s %s" % (sectionRows, sectionCols))
    self._iconColor   = 1
    self._inputProc   = None
    self._inputCtx    = None
    self._noInputProc   = None
    self._noInputCtx  = None
    self._cursor      = None
    self._msgWin      = None
    self._dcColors    = {}
    self._sections = [SectionInfo() for x in \
                      range(self._sectionRows*self._sectionCols)]
    self._testMode = False
    
  def createMainWindow(self):
    # Init curses mode
    self._mainWin = curses.initscr()
    curses.noecho()  # turn off key echo
    curses.cbreak()  # turn of input buffering
    self._mainWin.keypad(1) # Process function key escape sequences as single key events
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
    curses.curs_set(0)
        
    self._ttyCols = curses.COLS
    self._ttyRows = curses.LINES

    self._mainWin.clear()
    self._mainWin.refresh()
    
  def cursor(self):
    return self._cursor

  def destroyMainWindow(self):
    # Restore starting terminal state
    self._mainWin.keypad(0)
    curses.nocbreak()
    curses.echo()

    curses.endwin()

  def drawCell(self, row, col, icon, attrs=(0,0),drawIcons=True):
    cellH, cellW = 3,4
    select = curses.A_REVERSE if (row, col) == self._cursor else 0
    ulRow, ulCol = row*(cellH-1)+1, col*(cellW-1)+2

    corners = self._cellCorners(row, col)
    self._mainWin.addch(ulRow,   ulCol, corners[0], select)      # UL
    self._mainWin.addch(ulRow,   ulCol+1, curses.ACS_HLINE, select)
    self._mainWin.addch(ulRow,   ulCol+2, curses.ACS_HLINE, select)
    self._mainWin.addch(ulRow,   ulCol+3, corners[1], select)    # UR
    self._mainWin.addch(ulRow+1, ulCol, curses.ACS_VLINE, select)
    self._mainWin.addch(ulRow+1, ulCol+3, curses.ACS_VLINE, select)
    self._mainWin.addch(ulRow+2, ulCol, corners[2], select)      # LL
    self._mainWin.addch(ulRow+2, ulCol+1, curses.ACS_HLINE, select)
    self._mainWin.addch(ulRow+2, ulCol+2, curses.ACS_HLINE, select)
    self._mainWin.addch(ulRow+2, ulCol+3, corners[3], select)    # LR
    if drawIcons:
      iAttr = curses.A_BOLD
      pAttr = curses.A_REVERSE if icon[0] == 'P' else 0
      self._mainWin.addch(ulRow+1, ulCol+1, icon[0], attrs[0]|iAttr|pAttr)
      pAttr = curses.A_REVERSE if icon[1] == 'P' else 0
      self._mainWin.addch(ulRow+1, ulCol+2, icon[1], attrs[1]|iAttr|pAttr)

  def drawGrid(self):
    LOG.debug("DRAW GRID: COLS=%s" % self._sectionCols)
    for col in range(self._sectionCols):
      self._mainWin.addstr(0, col*3+3, "%02d" % col)
        
    for row in range(self._sectionRows):
      self._mainWin.addstr(row*2+2, 0, "%02d" % row)
        
    for idx, si in enumerate(self._sections):
      row = idx // self._sectionCols
      col = idx % self._sectionCols
      self.drawCell(row, col, si._icons, si._colors)

    self._mainWin.refresh()
    
  def mainLoop(self):
    cellRow = 0
    cellCol = 0
      
    input = ""
    curses.halfdelay(30)

    while input != "KEY_F(10)":
      try:
        input = self._mainWin.getkey()
      except curses.error as curx:
        if curx.message == 'no input':
          input = "<NoInput>"
          if self._noInputProc:
            self._noInputProc(self, self._noInputCtx)
        else:
          raise curx

      if self._inputProc:
        self._inputProc(self, input, self._inputCtx)

      if not self._testMode:
        continue
      
      if input == "KEY_UP" and cellRow > 0:
        cellRow -= 1
        self.moveCursor(-1, 0)
        self.printMsg("Grid Pos: [%s,%s]" % (cellRow, cellCol))
      elif input == "KEY_DOWN" and cellRow < self._sectionRows-1:
        cellRow += 1
        self.moveCursor(1, 0)
        self.printMsg("Grid Pos: [%s,%s]" % (cellRow, cellCol))
      elif input == "KEY_RIGHT" and cellCol < self._sectionCols-1:
        cellCol += 1
        self.moveCursor(0, 1)
        self.printMsg("Grid Pos: [%s,%s]" % (cellRow, cellCol))
      elif input == "KEY_LEFT" and cellCol > 0:
        cellCol -= 1
        self.moveCursor(0, -1)
        self.printMsg("Grid Pos: [%s,%s]" % (cellRow, cellCol))
      elif input == 'g':
        for row in range(self._sectionRows):
            for col in range(self._sectionCols):
#              si = SectionInfo(row, col, 0, state, "SJM", "DC1")
              self.drawCell(row, col, "XX")
      elif input == 'h':
        if self._cursor == (cellRow, cellCol):
          self.setCursor(None)
        else:
          self.setCursor(cellRow, cellCol)
        self.drawCell(cellRow, cellCol, "XX")
      elif input == 'c':
        self.drawCell(cellRow, cellCol, "XX")
      elif input == 'a':
        DrawACS(self._mainWin, 30, 0)
        self.printMsg("ACS_BBSS: %r" % curses.ACS_BBSS)
      elif input == 'm':
        if not self._msgWin:
          import msgwin
          self._msgWin = msgwin.MessageWin(self._mainWin, self._ttyRows-8, 0,
                                           self._ttyCols, 8)
          self._msgWin.setTitle("Debug")
        self._msgWin.hide() if self._msgWin.visible() else self._msgWin.show()
      elif input == 'r':
        self.resizeGrid(2,7)
      elif input != "<NoInput>":
        self.printMsg("INPUT: %r" % input)

  def mainWin(self):
    return self._mainWin
  
  def moveCursor(self, rowDelta, colDelta):
    if self._cursor is None:
      return
    curR, curC = self._cursor
    newR = min(max(curR+rowDelta,0),self._sectionRows-1)
    newC = min(max(curC+colDelta,0),self._sectionCols-1)
    self._cursor = None
    self.drawCell(curR, curC, "  ", drawIcons=False)
    self._cursor = (newR, newC)
    self.drawCell(newR, newC, "  ", drawIcons=False)
                    
  def printMsg(self, msg, row=1):
    if self._msgWin:
      self._msgWin.add(msg)

  def refresh(self):
    self._mainWin.touchwin()
    self._mainWin.refresh()
#    self._msgWin.touchwin()
#    self._msgWin.refresh()
    
  def resizeGrid(self, rows, cols):
    self._sectionRows = rows
    self._sectionCols = cols
    newSIs = [SectionInfo() for x in \
                      range(self._sectionRows*self._sectionCols)]
    for sidx in range(min(len(newSIs), len(self._sections))):
      newSIs[sidx] = self._sections[sidx]
    self._sections = newSIs
    self._mainWin.clear()
    self._mainWin.refresh()
    self.drawGrid()

  def setCursor(self, row, col=None):
    if self._cursor is not None:
        curR, curC = self._cursor
        self._cursor = None
        self.drawCell(curR, curC, "  ", drawIcons=False)
    if row is None:
      return
    self._cursor = (min(max(row,0),self._sectionRows-1),
                    min(max(col,0),self._sectionCols-1))
    self.drawCell(self._cursor[0], self._cursor[1], "  ", drawIcons=False)

  def setDCColors(self, dcColors):
    self._dcColors = dcColors
    
  def setInputCallback(self, callable, context):
    self._inputProc = callable
    self._inputCtx  = context

  def setMessageWin(self, msgWin):
    self._msgWin = msgWin
    
  def setNoInputCallback(self, callable, context):
    self._noInputProc = callable
    self._noInputCtx  = context

  def setSectionState(self, row, col, phase, state, sjm, dc):
    LOG.debug("setSectionState(%s, %s, %s, %s, %s, %s)" % (row, col, phase, state, sjm, dc))
    sdx = row * self._sectionCols + col
    section = self._sections[sdx]
    phase %= 2
    section._icons[phase] = self._stateIcon(state)
    section._colors[phase] = curses.color_pair(self._dcColors.get(dc, (0,0)))

  def ttySize(self):
    self._ttyCols = curses.COLS
    self._ttyRows = curses.LINES
    return (self._ttyRows, self._ttyCols)
  
  def _cellCorners(self, row, col):
    ll = ur = lr = curses.ACS_PLUS 
    if row == 0:
      ul = curses.ACS_ULCORNER if col == 0 else curses.ACS_TTEE
      ur = curses.ACS_TTEE if col < self._sectionCols-1 else curses.ACS_URCORNER
      if row < self._sectionRows-1:
        ll = curses.ACS_LTEE if col == 0 else curses.ACS_PLUS
        lr = curses.ACS_PLUS if col < self._sectionCols-1 else curses.ACS_RTEE
      else:
        ll = curses.ACS_LLCORNER if col == 0 else curses.ACS_BTEE
        lr = curses.ACS_BTEE if col < self._sectionCols-1 else curses.ACS_LRCORNER
    elif row > 0 and row < self._sectionRows-1:
      ul = curses.ACS_LTEE if col == 0 else curses.ACS_PLUS
      ur = curses.ACS_PLUS if col < self._sectionCols-1 else curses.ACS_RTEE
      ll = curses.ACS_LTEE if col == 0 else curses.ACS_PLUS
      lr = curses.ACS_PLUS if col < self._sectionCols-1 else curses.ACS_RTEE
    else:
      ul = curses.ACS_LTEE if col == 0 else curses.ACS_PLUS
      ur = curses.ACS_PLUS if col < self._sectionCols-1 else curses.ACS_RTEE
      ll = curses.ACS_LLCORNER if col == 0 else curses.ACS_BTEE
      lr = curses.ACS_BTEE if col < self._sectionCols-1 else curses.ACS_LRCORNER
      
    return (ul,ur, ll, lr)

  def _stateIcon(self, state):
    if self._stateIcons is None:
      self._stateIcons = {
          -128: 'F',   # FAILED
          -127: 'U',   # UNAVAILABLE 
            -3: 'X',   # CANCELLED
            -2: 'H',   # ONHOLD
            -1: 'D',   # DISCONNECTED curses.ACS_NEQUAL
             0: 'p',   # PREPROCESS
             1: 'a',   # ASSIGNING
             2: 'A',   # ASSIGNED
             3: 'P',   # PROCESSING
             4: 'C',   # COMPLETE
             5: '<',   # TRANSFERRING
             6: 'T',   # TRANSFERRED
             7: '&',   # POSTPROCESS
             8: 'S',   # SUCCESS
           126: curses.ACS_DIAMOND # ANY
        }
    return self._stateIcons.get(state, '*')


  
def DrawACS(win, row, col):
  win.addch(row, col+0,   curses.ACS_BBSS)  
  win.addch(row, col+1,   curses.ACS_BLOCK)
  win.addch(row, col+2,   curses.ACS_BOARD)
  win.addch(row, col+3,   curses.ACS_BSBS)
  win.addch(row, col+4,   curses.ACS_BSSB)
  win.addch(row, col+5,   curses.ACS_BSSS)
  win.addch(row, col+6,   curses.ACS_BTEE)
  win.addch(row, col+7,   curses.ACS_BULLET)
  win.addch(row, col+8,   curses.ACS_CKBOARD)
  win.addch(row, col+9,   curses.ACS_DARROW)
  win.addch(row, col+10,   curses.ACS_DEGREE)
  win.addch(row, col+11,   curses.ACS_DIAMOND)
  win.addch(row, col+12,   curses.ACS_GEQUAL)
  win.addch(row, col+13,   curses.ACS_HLINE)
  win.addch(row, col+14,   curses.ACS_LANTERN)
  win.addch(row, col+15,   curses.ACS_LARROW)
  win.addch(row, col+16,   curses.ACS_LEQUAL)
  win.addch(row, col+17,   curses.ACS_LLCORNER)
  win.addch(row, col+18,   curses.ACS_LRCORNER)
  win.addch(row, col+19,   curses.ACS_LTEE)
  win.addch(row, col+20,   curses.ACS_NEQUAL)
  win.addch(row, col+21,   curses.ACS_PI)
  win.addch(row, col+22,   curses.ACS_PLMINUS)
  win.addch(row, col+23,   curses.ACS_PLUS)
  win.addch(row, col+24,   curses.ACS_RARROW)
  win.addch(row, col+25,   curses.ACS_RTEE)
  win.addch(row, col+26,   curses.ACS_S1)
  win.addch(row, col+27,   curses.ACS_S3)
  win.addch(row, col+28,   curses.ACS_S7)
  win.addch(row, col+29,   curses.ACS_S9)
  win.addch(row, col+30,   curses.ACS_SBBS)
  win.addch(row, col+31,   curses.ACS_SBSB)
  win.addch(row, col+32,   curses.ACS_SBSS)
  win.addch(row, col+33,   curses.ACS_SSBB)
  win.addch(row, col+34,   curses.ACS_SSBS)
  win.addch(row, col+35,   curses.ACS_SSSB)
  win.addch(row, col+36,   curses.ACS_SSSS)
  win.addch(row, col+37,   curses.ACS_STERLING)
  win.addch(row, col+38,   curses.ACS_TTEE)
  win.addch(row, col+39,   curses.ACS_UARROW)
  win.addch(row, col+40,   curses.ACS_ULCORNER)
  win.addch(row, col+41,   curses.ACS_URCORNER)
  win.addch(row, col+42,   curses.ACS_VLINE)
  

def InitModuleLog():
  global LOG
  import logging.handlers
  LOG = logging.getLogger('sbmonitor')
  LOG.setLevel(logging.DEBUG)
  rfh = logging.handlers.RotatingFileHandler('sectiongrid.log',
                                             maxBytes=1024*1024,
                                             backupCount=5)
  rfh.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(module)s::%(funcName)s %(message)s')
  rfh.setFormatter(formatter)
  LOG.addHandler(rfh)



def main(argv):
  InitModuleLog()
  argv = sys.argv
  grid = SectionGrid(int(argv[1]), int(argv[2]))
  grid.createMainWindow()
  grid._testMode = True
  grid.mainLoop()
  grid.destroyMainWindow()
  
  
if __name__ == '__main__':
  curses.wrapper(main)
