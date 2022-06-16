#!/mingw64/bin/python3w.exe
# PyQt5 clipboard
#
# Gets text from the system clipboard
# If you copy text to the clipboard,
# output is shown in the console.
#
# pythonprogramminglanguage.com
#

import ast
import base64
import binascii
import functools
import os
import sys

from PyQt5.QtCore import QSize
from PyQt5.QtCore import QTimer
from PyQt5.Qt import QApplication
from PyQt5.Qt import QClipboard
from PyQt5.Qt import QVBoxLayout
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget

VERBOSE = True

class ExampleWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(440, 240))    
        self.setWindowTitle("PyQt5 Clipboard example") 

        # Add text field
        self.b = QPlainTextEdit(self)
        self.b.insertPlainText("Use your mouse to copy text to the clipboard.\nText can be copied from any application.\n")
 #       self.b.move(10,10)
#        self.b.resize(400,200)
 
        vbox = QVBoxLayout()
        centerW = QWidget()
        centerW.setLayout(vbox)
        self.setCentralWidget(centerW)


        self._openFileBTN = QPushButton("Open File...")
        self._openFileBTN.clicked.connect(self._openFileCB)
        vbox.addWidget(self._openFileBTN)

        vbox.addWidget(self.b)

        self._fsendPRG = QProgressBar()
        self._fsendPRG.setMaximum(100)
        vbox.addWidget(self._fsendPRG)

        self._dumpStateBTN = QPushButton("Dump State")
        self._dumpStateBTN.clicked.connect(self._dumpStateCB)
        vbox.addWidget(self._dumpStateBTN)

        self._cpyChunkBTN = QPushButton("Copy Chunck")
        self._cpyChunkBTN.clicked.connect(self.copyChunkCB)
        vbox.addWidget(self._cpyChunkBTN)

        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)

        self._xferState = "XFER_STATE_IDLE"
        self._chunkNum = 1
        self._fsendChunk = 0
        self._chunksSent = 0
        self._lastChunkProto = None

    # Get the system clipboard contents
    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        print(text)
#        self.b.insertPlainText("%s\n" % text)
        if self._isReplyProto(text):
            proto = ast.literal_eval(text[8:-8])
            print("PROTO = %s" % repr(proto))
            opcode = proto.get("opcode")
            if opcode == "FSENDACK" and \
               self._xferState == "XFER_STATE_WAIT_INIT_ACK":
                self._sendNextChunk()
            elif opcode == "CHUNKACK" and \
                 self._xferState == "XFER_STATE_WAIT_CHUNK_ACK":
                if int(proto.get("chunk")) == self._fsendChunk: 
                    self._fsendChunk += 1
                    self._sendNextChunk()
                    print("CHUNK ACK: %s" % self._fsendChunk)
                    self._fsendPRG.setValue(self._fsendChunk)
                else:
                    print("ERROR CHUNK ACK: pchunk=%s schunk=%s sent=%s" %
                          (int(proto.get("chunk")), self._fsendChunk, self._chunksSent))
#                    if self._lastChunkProto:
#                        self._timeoutProtoSendCB(self._lastChunkProto)
            else:
                print("XFERSTATE: %s" % self._xferState)
        else:
            print("NOPROTO: %r" % text)

    def copyChunkCB(self):
        print("copyChunkCB")
        chunk = chr(32+self._chunkNum) * 80
        QApplication.clipboard().setText(chunk)
        self._chunkNum += 1

    def _openFileCB(self):
#        dialog = QFileDialog(self)
#        dialog.exec_()
#        path = dialog.selectedFile()
#        print("Path: %s" % path)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if path:
            print("PATH: %s" % path)
            try:
                sbuf = os.stat(path)
                self._sendXferInit(path, sbuf.st_size)
            except OSError as iox:
                print("IOError: %s" % iox)

    def _sendXferInit(self, path, size):
        self._fsendPRG.setValue(0)
        self._fsendFP = open(path, "rb")
        self._fsendChunkMax = 32 * 1024
        chunks = size // self._fsendChunkMax
        if size % self._fsendChunkMax:
            chunks += 1
        self._fsendPRG.setMaximum(chunks)
        self.b.insertPlainText("FSEND: path=%s chunks=%s\n" % (path,chunks))
        self._fsendChunk = 0
        self._chunksSent = 0
        self._lastChunkProto  = None
        self._fsendSize  = size
        xferInitAttr = { "opcode":"FSEND", "path":path,
                         "chunksize":65536, "filesize":size }
        xferInitProto = ">>@@@@>>%s>>@@@@>>" % repr(xferInitAttr)
        self._xferState = "XFER_STATE_WAIT_INIT_ACK"
        QApplication.clipboard().setText(xferInitProto)

    def _sendNextChunk(self):
        print("_sendNextChunk")
        chunkBytes = self._fsendFP.read(self._fsendChunkMax)
        if chunkBytes:
            chunk64 = base64.standard_b64encode(chunkBytes)
            proto = { "opcode":"FSENDCHUNK", "chunk":self._fsendChunk,
                      "chunksize":len(chunkBytes), "chunktext":chunk64,
                      "chunkcrc":binascii.crc32(chunkBytes) }
            self._xferState = "XFER_STATE_WAIT_CHUNK_ACK"
            protostr = ">>@@@@>>%s>>@@@@>>" % repr(proto)
            thunk = functools.partial(self._timeoutProtoSendCB, protostr)
            QTimer.singleShot(300, thunk)
        else:
            proto = { "opcode":"FSENDCHUNK", "chunk":self._fsendChunk,
                      "chunksize":0, "chunktext":"", "EOF":"True" }
            self._xferState = "XFER_STATE_WAIT_CHUNK_ACK"
            protostr = ">>@@@@>>%s>>@@@@>>" % repr(proto)
            thunk = functools.partial(self._timeoutProtoSendCB, protostr)
            QTimer.singleShot(300, thunk)
            self._fsendFP.close()

    def _isReplyProto(self, text):
        if text[0:8] == "<<@@@@<<" and text[-8:] == "<<@@@@<<":
            return True

    def _timeoutProtoSendCB(self, protostr):
        print("PROTOSTR: %s" % protostr)
        self._lastChunkProto = protostr
        QApplication.clipboard().setText(protostr)
        self._chunksSent += 1

    def _dumpStateCB(self):
        print("STATE: %r chunk=%s sent=%s" %
              (self._xferState, self._fsendChunk, self._chunksSent))

    def appendText(self, text):
        self.b.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        self.b.insertPlainText("%s\n" % text)
        self;_inputTE.ensureCursorVisible()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit( app.exec_() )
