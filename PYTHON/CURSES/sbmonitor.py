#!/usr/local/anaconda2/bin/python

import curses
import os
import subprocess
import sys

import confirmdlg
import dialog
import msgwin
import optiondlg
import sbstatefile
import sectiongrid

__LOGFP = None #open("sbmonitor.log", "w")
def LOG(msg):
  global __LOGFP
  if __LOGFP:
    __LOGFP.write(msg+"\n")
    __LOGFP.flush()


class SBMonitor(object):

  def __init__(self, jobPath, sbuPath):
    self._jobPath = jobPath
    self._sbuPath = sbuPath

    jobSBPath = os.path.join(jobPath, "sectionjob", "sb")
    stateFile = os.path.join(jobSBPath, "sbconfig.astate")
    self._sbState = sbstatefile.TableFileStore(jobSBPath, bkupSuffix='', writable=False, useCheckSum=False)
    self._kvData = {}
    assignments  = []
    states       = []
    self._sbState.Load(self._kvData, assignments, states)

    self._secRows = int(self._kvData.get('SECTION_ROWS', -1))
    self._secCols = int(self._kvData.get('SECTION_COLS', -1))

    self._grid = sectiongrid.SectionGrid(self._secRows, self._secCols)
    self._grid.setInputCallback(self._userInput, self)
    self._grid.setNoInputCallback(self._reloadState, self)

    self._selecting = False
    self._ESC = '\x1b'
    
    self._msgWin     = None
    self._helpWin    = None
    self._dcColorWin = None
    self._sbutilWin  = None
    self._symbolWin  = None
    
  def main(self, stdscr):
    self._grid.createMainWindow()
    ttySize = self._grid.ttySize()
    self._msgWin = msgwin.MessageWin(self._grid.mainWin(), ttySize[0]-8, 0, ttySize[1], 8)
    self._msgWin.setTitle("Messages:")
    self._grid.setMessageWin(self._msgWin)

    self._grid.mainWin().addstr(ttySize[0]-1, 2, "? For Help")

    self._grid.mainLoop()

    self._grid.destroyMainWindow()

  def selectDrainTarget(self):
    ttyRows, ttyCols = self._grid.ttySize()
    dcNum = int(self._kvData.get("DC_NUM", "0"))
    dlgW, dlgH = 48, dcNum+3
    dlg = optiondlg.OptionDialog(self._grid.mainWin(),
                                 (ttyRows-dlgH)//2, (ttyCols-dlgW)//2,
                                 dlgW, dlgH)
    dlg.setTitle(" Drain Data Centor ")
    options = []
    for dcx in range(dcNum):
      dcUUID = self._kvData.get("DC_ID_%s" % dcx, "<NO ENTRY>")
      options.append("DC(%02d) - %s" % (dcx, dcUUID))
    options.append("CANCEL")
    dlg.setOptions(options)
    dlg.selectOption("CANCEL")
    dlg.show()
    choice = dlg.browseOptions()
    dlg.hide()
    if choice and choice[1] != "CANCEL":
      dcUUID = self._kvData.get("DC_ID_%s" % choice[0], "<NO ENTRY>")
      self.showDCDrain(dcUUID)
        
  def showDCColorWin(self):
    if not self._dcColorWin:
      ttyRows, ttyCols = self._grid.ttySize()
      dcNum = int(self._kvData.get("DC_NUM", "0"))
      dlgW, dlgH = ttyCols - 4, 12
      win = dialog.DialogWin(self._grid.mainWin(), (ttyRows-dlgH)//2, (ttyCols-dlgW)//2, dlgW, dlgH)
      win.setTitle("Data Centor Colors")
      for dc in range(dcNum):
        dcUUID = self._kvData.get("DC_ID_%s" % dc, "<NO ENTRY>")
        dcPath = self._kvData.get("DC_PATH_%s" % dcUUID, "<NO ENTRY>")
        attr = curses.color_pair(dc+1) | curses.A_BOLD
        win.addLabel("DC(%s) - %s" % (dc,dcUUID), dc*2+1, 2, attr)
        win.addLabel(" %s" % dcPath, dc*2+2, 2, attr)
      self._dcColorWin = win
    self._dcColorWin.show()
    input = ""
    while input != self._ESC:
      input = self._dcColorWin.read()
    self._dcColorWin.hide()

  def showDCDrain(self, dcUUID):
    self._showSBUtilWin(["-r", "-c", dcUUID], "Drain DC %s" % dcUUID)

  def showHelpWin(self):
    if not self._helpWin:
      ttyRows, ttyCols = self._grid.ttySize()
      self._helpWin = dialog.DialogWin(self._grid.mainWin(), (ttyRows-20)//2, (ttyCols-60)//2, 60, 20)
      self._helpWin.setTitle("SBMonitor Help")
      self._helpWin.addLabel("S   - Show SB State Counters", 1, 2)
      self._helpWin.addLabel("P   - Show DC Job Phase Summary", 2, 2)
      self._helpWin.addLabel("H   - Show A Section State History", 3, 2)
      self._helpWin.addLabel("F   - Show Section Failures", 4, 2)
      self._helpWin.addLabel("I   - Show SB Server Info", 5, 2)
      self._helpWin.addLabel("D   - Drain A Data Center", 6, 2)
      self._helpWin.addLabel("Q   - Shutdown Job", 7, 2)
      self._helpWin.addLabel("*   - Show DC Color Table", 14, 2)
      self._helpWin.addLabel("!   - Show Symbol Definitions", 15, 2)
      self._helpWin.addLabel("M   - Show Diagnostic Messages", 16, 2)
      self._helpWin.addLabel("ESC - Dismiss Dialog (including this one)", 17, 2)
      self._helpWin.addLabel("F10 - Exit SBMonitor", 18, 2)
    self._helpWin.show()
    input = ""
    while input != self._ESC:
      input = self._helpWin.read()
    self._helpWin.hide()
      
  def showMessageWin(self):
    self._msgWin.show()
    self._msgWin.browse()

  def showSectionHistory(self, sid):
    self._showSBUtilWin(["secjobs", "--history", sid], "Section %s History"%sid)
  
  def showSectionStates(self):
    self._showSBUtilWin(["secjobs"], "SBUtil Section State Counts")

  def showPhaseSummary(self):
    self._showSBUtilWin(["secjobs", "--summary"], "SBUtil Phase Summary")

  def showServerInfo(self):
    self._showSBUtilWin(["srvrinfo"], "SB Server Info")

  def showSectionFailures(self):
    self._showSBUtilWin(["secjobs", "--fail"], "Section Process Failures")

  def showSymbolWin(self):
    if not self._symbolWin:
      ttyRows, ttyCols = self._grid.ttySize()
      win = dialog.DialogWin(self._grid.mainWin(), (ttyRows-20)//2, (ttyCols-60)//2, 60, 20)
      win.setTitle("SBMonitor Symbols")
      win.addSymbol(curses.ACS_ULCORNER, 1, 1)
      win.addSymbol(curses.ACS_HLINE,    1, 2)
      win.addSymbol(curses.ACS_HLINE,    1, 3)
      win.addSymbol(curses.ACS_URCORNER, 1, 4)
      win.addSymbol(curses.ACS_VLINE,    2, 1)
      win.addSymbol(curses.ACS_CKBOARD,  2, 2, curses.color_pair(1)|curses.A_BOLD)
      win.addSymbol(curses.ACS_CKBOARD,  2, 3, curses.color_pair(2)|curses.A_BOLD)
      win.addSymbol(curses.ACS_VLINE,    2, 4)
      win.addSymbol(curses.ACS_LLCORNER, 3, 1)
      win.addSymbol(curses.ACS_HLINE,    3, 2)
      win.addSymbol(curses.ACS_HLINE,    3, 3)
      win.addSymbol(curses.ACS_LRCORNER, 3, 4)
      win.addSymbol(curses.ACS_CKBOARD,  2, 8, curses.color_pair(1)|curses.A_BOLD)
      win.addLabel("- Phase 0 State", 2, 10)
      win.addSymbol(curses.ACS_CKBOARD,  2, 27, curses.color_pair(2)|curses.A_BOLD)
      win.addLabel("- Phase 1 State", 2, 29)
      win.addLabel("State Symbols:",   4, 2)
      win.addLabel("F - FAILED",       5, 4)
      win.addLabel("U - UNAVAILABLE",  6, 4) 
      win.addLabel("X - CANCELLED",    7, 4)
      win.addLabel("H - ONHOLD",       8, 4)
      win.addLabel("D - DISCONNECTED", 9, 4)  # curses.ACS_NEQUAL
      win.addLabel("p - PREPROCESS",   10, 4)
      win.addLabel("a - ASSIGNING",    11, 4)
      win.addLabel("A - ASSIGNED",     12, 4)
      win.addLabel("P - PROCESSING",   13, 4)
      win.addLabel("C - COMPLETE",     14, 4)
      win.addLabel("< - TRANSFERRING", 15, 4)
      win.addLabel("T - TRANSFERRED",  16, 4)
      win.addLabel("& - POSTPROCESS",  17, 4)
      win.addLabel("S - SUCCESS",      18, 4)
      win.addLabel("Symbol Colors Indicate DC Location", 4, 24)
      self._symbolWin = win
    self._symbolWin.show()
    input = ""
    while input != self._ESC:
      input = self._symbolWin.read()
    self._symbolWin.hide()

  def shutdownJob(self):
    dlgW, dlgH = 40, 12
    ttyRows, ttyCols = self._grid.ttySize()
    dlg = confirmdlg.ConfirmDialog(self._grid.mainWin(),
                                   (ttyRows-dlgH)//2, (ttyCols-dlgW)//2,
                                   dlgW, dlgH)
    dlg.setButtons(["NO", "YES"])
    dlg.setTitle(" Confirm Shutdown ")
    dlg.setText("Are you sure you want to shutdown?")
    dlg.setFocus("NO")
    dlg.show()
    choice = dlg.browseOptions()
    dlg.hide()
    if choice and choice[1] == "YES":
      self._showSBUtilWin(["shutdown"], "SBUtil Shutdown")
    
  def _reloadState(self, grid, sbMon):
    if self._selecting:
      return
    
    kvData = {}
    assignments = []
    states = []
    self._sbState.Rewind()
    self._sbState.Load(kvData, assignments, states)

    aidTable = {}
    dcTable  = {}
    dcColor = 1
    for aid in assignments:
      key = (aid._row,aid._col,aid._phase,aid._assignId)
      aidTable[key] = (aid._SJM, aid._DC)
      if not dcTable.get(aid._DC):
        dcTable[aid._DC] = dcColor
        dcColor += 1

    self._grid.setDCColors(dcTable)
      
    for sr in states:
      key = (sr._row,sr._col,sr._phase,sr._assignId)
      sjm, dc = aidTable.get(key, (None, None))
      self._grid.setSectionState(sr._row, sr._col, sr._phase, sr._stateId, sjm, dc)

    self._grid.drawGrid()

  def _showSBUtilWin(self, cmd, title):
    ttyRows, ttyCols = self._grid.ttySize()
    LOG("RESIZED: %s %s %s" % (curses.is_term_resized(ttyRows, ttyCols), ttyRows, ttyCols))
    if not self._sbutilWin:
      ttyRows, ttyCols = self._grid.ttySize()
      winW = max(78, int(ttyCols*0.8))
      winH = max(24, int(ttyRows*0.8))
      winR = (ttyRows-winH) // 2
      winC = (ttyCols-winW) // 2
      win = msgwin.MessageWin(self._grid.mainWin(), winR, winC, winW, winH)
      win.setTitle(title)
      self._sbutilWin = win
    self._sbutilWin.clear()
    if not self._sbuPath:
      self._sbutilWin.add("ERROR: No TFlex Root Specified")
    else:
      cmd = [self._sbuPath, "-d", self._jobPath] + cmd
      try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as subx:
        output = "ERROR: %s\n%s" % (subx.returncode, subx.output)
      for line in output.split("\n"):
        self._sbutilWin.add(line)
    self._sbutilWin.show()
    self._sbutilWin.browse()

  def _userInput(self, grid, input, sbMon):
    ttyRows, ttyCols = self._grid.ttySize()
    resized = curses.is_term_resized(ttyRows, ttyCols)
    if resized:
       newRows, newCols = self._grid.mainWin().getmaxyx()
       self._grid.mainWin().clear()
       curses.resizeterm(newRows, newCols)
       self._grid.mainWin().refresh()
    
    if input == "?":
      self.showHelpWin()
    elif input.upper() == "S":
      self.showSectionStates()
    elif input.upper() == "P":
      self.showPhaseSummary()
    elif input.upper() == "I":
      self.showServerInfo()
    elif input.upper() == "F":
      self.showSectionFailures()
    elif input.upper() == "Q":
      self.shutdownJob()
    elif input.upper() == "D":
      self.selectDrainTarget()
    elif input.upper() == "H":
      #self.sectionHistory()
      self._grid.setCursor(0,0)
      self._selecting = "SELECT:SECTHISTORY"
    elif input == "\n":
      if self._selecting == "SELECT:SECTHISTORY":
        self._msgWin.add("Select Section %r" % (self._grid.cursor(),))
        row,col = self._grid.cursor()
        sid = "%03d_%03d" % (col, row)
        self._selecting = None
        self._grid.setCursor(None)
        self.showSectionHistory(sid)
      
    elif input.upper() == "M":
      self.showMessageWin()
      
    elif input.upper() == "*":
      self.showDCColorWin()
      
    elif input.upper() == "!":
      self.showSymbolWin()
      
    elif input == "/":
      self._grid.drawCell(0, 0, "!!", highlight=True)
      
    elif self._selecting:
      if input == "KEY_UP":
        self._grid.moveCursor(-1, 0)
      elif input == "KEY_DOWN":
        self._grid.moveCursor(1, 0)
      elif input == "KEY_RIGHT":
        self._grid.moveCursor(0, 1)
      elif input == "KEY_LEFT":
        self._grid.moveCursor(0, -1)


if __name__ == "__main__":
  jobPath = sys.argv[1]

  sbuPath = None
  if len(sys.argv) >= 3:
    tflexRoot = sys.argv[2]
    sbup = os.path.join(tflexRoot, "bin/sbutil")
    if os.path.exists(sbup):
      sbuPath = sbup
      
  sbMonitor = SBMonitor(jobPath, sbuPath)
  
  curses.wrapper(sbMonitor.main)
