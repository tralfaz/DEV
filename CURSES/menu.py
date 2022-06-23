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


def main(stdscr=None, *args):
  if not stdscr:
    stdscr = curses.initscr()

  curses.noecho() # turn off key echo
  curses.cbreak() # turn of input buffering
  stdscr.keypad(1) # Process function key escape sequences as single key events

#  stdscr.addstr(0, 0, "Current mode, Typing mode", curses.A_REVERSE)
#  pad = test_pad()
  stdscr.border(0)
  CenterLine(stdscr, "Hello, World!")
  # pad.refresh(0, 0, 5, 5, 20, 75)
  stdscr.refresh()

  markRow = markCol = 1
  stdscr.move(markRow, markCol)
  stdscr.addstr("#")

  while True:
    key = stdscr.getch()
    if key == ord('q'):
      break
    elif key == curses.KEY_LEFT:
      stdscr.move(markRow, markCol-1)
      stdscr.addstr("# ")
      markCol -= 1
    elif key == curses.KEY_RIGHT:
      stdscr.move(markRow, markCol)
      stdscr.addstr(" #")
      markCol += 1

  # Restore starting terminal state
  stdscr.keypad(0)
  curses.nocbreak()
  curses.echo()

  windir = dir(stdscr)
  maxRowCol = stdscr.getmaxyx()
  curdir = dir(curses)

  curses.endwin()

  print windir
  print curdir
  print repr(maxRowCol)

curses.wrapper(main)
