import curses
import curses.wrapper
import getpass
import os
import subprocess

#LOG = file('p4climenu.log', 'w')


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


def P4Login():
  cmd = ['/p4/current/p4', 'login']
  attempts = 0
  while attempts < 3:
    p4pswd = getpass.getpass('P4 Login: ')
    p4proc = subprocess.Popen(cmd, bufsize=8192,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              close_fds=True)
    p4proc.communicate(p4pswd)
    p4sts = p4proc.wait()
    if p4sts == 0:
      return True
    print 'P4 LOGIN Failed: %s' % p4sts
    attempts += 1
  return False


def GetUserClients(username):
  cmd = ['/p4/current/p4', 'clients', '-u', username]
  p4proc = subprocess.Popen(cmd, bufsize=8192,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=True)
  p4sts = p4proc.wait()
  #print "DEBUG: p4sts %r" % p4sts
  if p4sts:
    p4errout = p4proc.stderr.read()
    #print "DEBUG: p4errout %r" % p4errout
    if 'P4PASSWD' in p4errout or 'session has expired' in p4errout:
      return (False, 'P4PASSWD')
  else:
    return (True, p4proc.stdout.read())


if __name__ == '__main__':
  status, output = GetUserClients(getpass.getuser())
  if status is False and output == 'P4PASSWD':
    if P4Login():
      status, output = GetUserClients(getpass.getuser())
  if status and output:
    lines = output.split('\n')
    choices = []
    for line in lines:
      fields = line.split()
#      LOG.write('FIELDS: %r\n' % fields)
      if len(fields) > 5 and fields[0] == 'Client' and fields[3] == 'root':
        cliName, cliRoot = fields[1], fields[4]
        choices.append((cliName,cliRoot))
    
    if choices:
#      LOG.write('CHOICES: %r\n' % (choices))
      choice = ClientMenu(choices)
      if choice != 'Exit':
        choice_out = 'export P4CLIENT="%s"\n' % choice
      else:
        choice_out = '\n'

      path = os.path.join(os.getenv('HOME'), '.p4clientchoice.out')
      with file(path, 'w') as choiceFP:
        choiceFP.write(choice_out)
