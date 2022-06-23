import curses
import curses.wrapper


def test_pad():
  pad = curses.newpad(100, 100)

  # fill pad with test pattern
  for row in xrange(0,100):
    for col in xrange(0,100):
      try:
	pad.addch(row, col, ord('a') + (col*col+row*row) % 25)
      except curses.error:
        pass

    # displays a section of the pad in the middle of the screen
    pad.refresh(0, 0, 5, 5, 20, 75)
    return pad


def CenterLine(win, line):
  maxRows, maxCols = win.getmaxyx()
  row = maxRows // 2
  col = (maxCols - len(line)) // 2
  win.move(row, col)
  win.addstr(line)



def CreateWindow(row, col, height, width):
  win = curses.newwin(height, width, row, col)
  # 0,0 gives default characters for the vertical and horizonatal lines
  win.box(0, 0)
  win.refresh()  # Show the box
  return win
  
def DeleteWindow(win):
  # win.box(' ', ' ')  Won't yield the desired results of erasing the window.
  # It will leave its four corners.
  win.border(' ', ' ', # left, right side chars
             ' ', ' ', # top, bottom side chars
             ' ', ' ', # top-left, top-right chars
             ' ', ' ') # bottom-left, bottom-right chars
  win.refresh()
  del win
  
  
def main(stdscr=None, *args):
  outfp = file('vtout.txt', 'w')

  if not stdscr:
    stdscr = curses.initscr()

  curses.noecho() # turn off key echo
  curses.cbreak() # turn of input buffering
  stdscr.keypad(1) # Process function key escape sequences as single key events

  winH = 3
  winW = 10
  winR = (curses.LINES - winH) // 2
  winC = (curses.COLS - winW) // 2
  stdscr.addstr("Press F1 to exit")
  stdscr.refresh()
  myWin = curses.newwin(winH, winW, winR, winC)

  while True:
    key = stdscr.getch()
    outfp.write('KEY: %r %s\n' % (key, key))
    if key == curses.KEY_LEFT:
      DeleteWindow(myWin)
      winC -= 1
      myWin = CreateWindow(winR, winC, winH, winW)
    elif key == curses.KEY_RIGHT:
      DeleteWindow(myWin)
      winC += 1
      myWin = CreateWindow(winR, winC, winH, winW)
    elif key == curses.KEY_UP:
      DeleteWindow(myWin)
      winR -= 1
      myWin = CreateWindow(winR, winC, winH, winW)
    elif key == curses.KEY_DOWN:
      DeleteWindow(myWin)
      winR += 1
      myWin = CreateWindow(winR, winC, winH, winW)
    elif key == curses.KEY_F1:
      break

  # Restore starting terminal state
  stdscr.keypad(0)
  curses.nocbreak()
  curses.echo()

  curses.endwin()


curses.wrapper(main)
