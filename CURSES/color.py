import curses
#import curses.wrapper
import sys

def PrintInCenter(win, text):
  winRows, winCols = win.getmaxyx()
  txtRow = winRows // 2
  txtCol = (winCols - len(text)) // 2
  win.move(txtRow, txtCol)
  win.addstr(text)
  

def main(stdscr=None, *args):
  if not stdscr:
    stdscr = curses.initscr()

  if not curses.has_colors():
    curses.endwin()
    print "Your terminal does not support color"
    sys.exit(1)
    
  curses.start_color()
  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.noecho() # turn off key echo
  curses.cbreak() # turn of input buffering
  stdscr.keypad(1) # Process function key escape sequences as single key events

  stdscr.attron(curses.color_pair(1))
  PrintInCenter(stdscr, "Viola !!! In color ...")
  stdscr.refresh()
  stdscr.attroff(curses.color_pair(1))

  stdscr.getch()

  # Restore starting terminal state
  stdscr.keypad(0)
  curses.nocbreak()
  curses.echo()

  curses.endwin()


if __name__ == "__main__":
  curses.wrapper(main)
