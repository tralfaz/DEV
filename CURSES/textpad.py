import curses
import curses.wrapper
import getpass
import os
import subprocess
import sys

LOG = file('sectiongridlog', 'w')


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
#    LOG.write('CHOICE: %s\n' % choice[0])
    if highlight == cdx + 1:
      # highlight current choice
      win.attron(curses.A_REVERSE)
      win.move(y, x)
      win.addstr(choice[0])
      win.attroff(curses.A_REVERSE)
    else:
      win.move(y, x)
      win.addstr('%s' % choice[0])
    y += 1
  win.refresh()
        
  
def DrawCell(win, row, col, icon):
  win.addch(row, col, curses.ACS_ULCORNER)
  win.addch(row, col+1, curses.ACS_HLINE)
  win.addch(row, col+2, curses.ACS_HLINE)
  win.addch(row, col+3, curses.ACS_URCORNER)
  win.addch(row+1, col, curses.ACS_VLINE)
  win.addch(row+1, col+3, curses.ACS_VLINE)
  win.addch(row+2, col, curses.ACS_LLCORNER)
  win.addch(row+2, col+1, curses.ACS_HLINE)
  win.addch(row+2, col+2, curses.ACS_HLINE)
  win.addch(row+2, col+3, curses.ACS_LRCORNER)
  win.addch(row+1, col+1, icon[0])
  win.addch(row+1, col+2, icon[1])

def DrawGrid(rows, cols):

  # Init curses mode
  stdscr = curses.initscr()
  curses.noecho()  # turn off key echo
  curses.cbreak()  # turn of input buffering
  stdscr.keypad(1) # Process function key escape sequences as single key events

  termCols = curses.COLS
  termRows = curses.LINES

  stdscr.clear()

  # Create message win at bottom
  msgWinW = termCols
  msgWinH = 6
  msgWinC = 0
  msgWinR = termRows - msgWinH
  msgWin = curses.newwin(msgWinH, msgWinW, msgWinR, msgWinC) 

  stdscr.refresh()
  msgWin.refresh()

  pad = curses.newpad(100, 100)

  # These loops fill the pad with letters; addch() is
  # explained in the next section
  for y in range(0, 99):
    for x in range(0, 99):
      pad.addch(y,x, ord('a') + (x*x+y*y) % 26)

  # Displays a section of the pad in the middle of the screen.
  # (0,0) : coordinate of upper-left corner of pad area to display.
  # (5,5) : coordinate of upper-left corner of window area to be filled
  #         with pad content.
  # (20, 75) : coordinate of lower-right corner of window area to be
  #          : filled with pad content.
  pad.refresh(0,0, 5,5, 20,75)
  padX, padY = 0, 0
  padULX, padULY = 5, 5
  padLRX, padLRY = 75, 20
  input = ""
  curses.halfdelay(30)
  movePad = False
  while input != "KEY_F(10)":
    try:
      input = stdscr.getkey()
      if input == 'p':
        movePad = not movePad
        msgWin.clear()
        msgWin.addstr(1,1, "MOVEPAD %s" % movePad)
      elif input == "KEY_UP" and movePad:
        padY -= 1
        #pad.mvderwin(padY, padX)
        pad.refresh(padY, padX, padULY, padULX, padLRY, padLRX)
        msgWin.erase()
        msgWin.addstr(1,1, "PAD(%s, %s, %s, %s, %s, %s)" % (padY, padX, padULY, padULX, padLRY, padLRX))
        stdscr.refresh()
      elif input == "KEY_DOWN" and movePad:
        padY += 1
        #pad.mvderwin(padY, padX)
        pad.refresh(padY, padX, padULY, padULX, padLRY, padLRX)
        msgWin.clear()
        msgWin.addstr(1,1, "PAD(%s, %s, %s, %s, %s, %s)" % (padY, padX, padULY, padULX, padLRY, padLRX))
        stdscr.refresh()
      elif input == 'h':
        stdscr.hline(30,0,curses.ACS_HLINE,30)
      elif input == 'v':
        stdscr.vline(20,15,curses.ACS_VLINE,20)
      elif input == 'b':
        box1 = stdscr.subwin(3, 4, 30, 0)
        box1.box()
        box1.addstr(1,1, 'XX')
        box1.refresh()
        stdscr.refresh()
      elif input == 'B':
        box2 = stdscr.subwin(3, 4, 30, 3)
        box2.box()
        box2.addstr(1,1, '**')
        box2.refresh()
        stdscr.refresh()
      elif input == 'c':
        stdscr.addch(30, 10, curses.ACS_ULCORNER)
        stdscr.addch(30, 11, curses.ACS_HLINE)
        stdscr.addch(30, 12, curses.ACS_URCORNER)
        stdscr.addch(31, 10, curses.ACS_VLINE)
        stdscr.addch(32, 10, curses.ACS_LLCORNER)
        stdscr.addch(32, 11, curses.ACS_HLINE)
        stdscr.addch(32, 12, curses.ACS_PLUS)
      elif input == 'C':
        DrawCell(stdscr, 0, 0)
      else:
        msgWin.clear()
        msgWin.addstr(1,1, input)
      msgWin.refresh()
        
    except curses.error as curx:
      hdelay = curx
      if curx.message == 'no input':
        noInput = True
      
  # Restore starting terminal state
  stdscr.keypad(0)
  curses.nocbreak()
  curses.echo()

  curses.endwin()
   
  print "%s X %s" % (termRows, termCols)
  print "INPUT: %r" % input
  print "HDELAY: %r (%s)" % (dir(hdelay), hdelay)
  print "NoInput: %r" % noInput
  
  
def ClientMenu(choices):
  stdscr = curses.initscr()

  choices.append( ('Exit', ''))
  curses.noecho()  # turn off key echo
  curses.cbreak()  # turn of input buffering
  stdscr.keypad(1) # Process function key escape sequences as single key events

  MENU_W = 60
  MENU_H = 15
  
  startX = (curses.COLS  - MENU_W) // 2
  startY = (curses.LINES - MENU_H) // 2

  menuWin = curses.newwin(MENU_H, MENU_W, startY, startX)
  stdscr.move(0,0)
  stdscr.addstr("Use arrow keys to go up and down, "
                "Press enter to select a choice")
  stdscr.refresh()

  highlight = 1
  nchoices  = len(choices)
#  choices   = ["Choice 1", "Choice 2", "Choice 3", "Choice 4", "Exit"]
#  choices = args['choices']
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
  return choices[selection-1][0]


def main(argv):
  argv = sys.argv
  DrawGrid(3,2)    
  
if __name__ == '__main__':
  curses.wrapper(main)
#      LOG.write('FIELDS: %r\n' % fields)
#      LOG.write('CHOICES: %r\n' % (choices))
