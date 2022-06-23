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


def PrintMenu(win, choices, highlight):
  x = 2
  y = 2
  win.box(0, 0)
  for cdx, choice in enumerate(choices):
    if highlight == cdx + 1:
      # highlight current choice
      win.attron(curses.A_REVERSE)
      win.move(y, x)
      win.addstr(choice)
      win.attroff(curses.A_REVERSE)
    else:
      win.move(y, x)
      win.addstr(choice)
    y += 1
  win.refresh()
        
  
def main(stdscr=None, *args):
  if not stdscr:
    stdscr = curses.initscr()

  curses.noecho() # turn off key echo
  curses.cbreak() # turn of input buffering
  stdscr.keypad(1) # Process function key escape sequences as single key events

  MENU_W = 30
  MENU_H = 10
  
  startX = (curses.COLS  - MENU_W) // 2
  startY = (curses.LINES - MENU_H) // 2

  menuWin = curses.newwin(MENU_H, MENU_W, startY, startX)
  stdscr.move(0,0)
  stdscr.addstr("Use arrow keys to go up and down, "
                "Press enter to select a choice")
  stdscr.refresh()

  highlight = 1
  nchoices  = 5
  choices   = ["Choice 1", "Choice 2", "Choice 3", "Choice 4", "Exit"]
  PrintMenu(menuWin, choices, highlight)

  selection = 0
  while True:
    key = stdscr.getch()
    if key == curses.KEY_UP:
      if highlight == 1:
        highlight = nchoices
      else:
        highlight -= 1
    elif key == curses.KEY_DOWN:
      if highlight == nchoices:
        highlight = 1
      else:
        highlight += 1
    elif key == 10:
      selection = highlight
      break
    else:
      stdscr.move(curses.LINES, curses.COLS)
      stdscr.addstr("Character pressed is 0x%02x" % ord(key))

    PrintMenu(menuWin, choices, highlight)
    if selection:
      break

  stdscr.move(curses.LINES-1, 0)
  stdscr.addstr("You chose option %s" % selection)

  # Restore starting terminal state
  stdscr.keypad(0)
  curses.nocbreak()
  curses.echo()

  curses.endwin()
  print "You chose option %s" % selection

if __name__ == "__main__":
  curses.wrapper(main)
