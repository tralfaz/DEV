#!/usr/local/anaconda2/bin/python
from __future__ import print_function

import ast
import base64
import binascii
import functools
import os
import sys

from PyQt4.Qt import pyqtSignal
from PyQt4.Qt import QTimer
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QWidget

OPT_VERBOSE = True

class ExampleWindow(QMainWindow):

    sendXferProtoAck = pyqtSignal(str)

    def __init__(self):
        super(ExampleWindow,self).__init__()

        self.setMinimumSize(QSize(440,240))
        self.setWindowTitle("Clipboard Example")

	vbox = QVBoxLayout()

	centerW = QWidget()
	self.setCentralWidget(centerW)

        self._inputTE = QPlainTextEdit(self)
        self._inputTE.insertPlainText("Use your mouse to copy text to the "
                                      "clipboard.\nText can be copied from "
                                      "any application.\n")
        self._inputTE.move(10,10)
        self._inputTE.resize(400,200)
	vbox.addWidget(self._inputTE)

	self._copyChunkBTN = QPushButton("Copy Chunk")
	self._copyChunkBTN.clicked.connect(self._copyChunkCB)
	vbox.addWidget(self._copyChunkBTN)

	centerW.setLayout(vbox)

        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)

        self._overdueTMR = QTimer()
        self._overdueTMR.timeout.connect(self._overdueCB)
        
        self.sendXferProtoAck.connect(self._sendXferProtoAckCB)
        
        self._state = "XFER_STATE_IDLE"
	self._overdueFlipFlop = 0
     
    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        if OPT_VERBOSE:
            print(text)
        if self._isSendProto(text):
            protos = str(text[8:-8])
            if OPT_VERBOSE:
                print("SENDPROTO: %r" % protos)
            protod = ast.literal_eval(protos)
            opcode = protod.get("opcode")
            if opcode == "FSEND":
                self._overdueFlipFlop = 0
                self._fsendPath      = protod.get("path")
                self._fsendFileSize  = protod.get("filesize")
                self._fsendFP        = open(os.path.basename(self._fsendPath), "wb")
                self._fsendChunk     = 0
                self._fsendChunkSize = protod.get("chunksize")
                self._xferState = "XFER_STATE_AWAIT_CHUNK"
                self._sendFSendAck()

            elif opcode == "FSENDCHUNK":
                self._overdueTMR.stop()
                self._overdueFlipFlop = 0
                chunk = int(protod.get("chunk"))
                chunkText  = protod.get("chunktext")
                chunkSize  = int(protod.get("chunksize"))
                chunkBytes = base64.standard_b64decode(chunkText)
                chunkCRC   = protod.get("chunkcrc")
                bytesCRC   = binascii.crc32(chunkBytes) % (1<<32)
                chunkEOF   = bool(protod.get("EOF"))
                self.appendText("CHUNK: %s len=%s" % (chunk, len(chunkBytes)))
                if self._fsendChunk == chunk:
                    if chunkEOF:
                        self._fsendFP.close()
                        self._xferState = "XFER_STATE_IDLE"
                    else:
                        if chunkCRC != bytesCRC:
                            print("CRC ERROR: %s (%s)" % (chunkCRC, bytesCRC))
                        self._fsendFP.write(chunkBytes)
                        self._sendChunkAck(chunk)
                        self._fsendChunk += 1
                
    def _isSendProto(self, text):
        if text[0:8] == ">>@@@@>>" and text[-8:] == ">>@@@@>>":
            return True
        
    def _copyChunkCB(self):
        QApplication.clipboard().setText("TEXT CHUNK")

    def _sendFSendAck(self):
        proto = { "opcode":"FSENDACK"}
        ack = "<<@@@@<<%s<<@@@@<<" % repr(proto)
        thunk = functools.partial(self._sendXferProtoAckCB, ack)
        QTimer.singleShot(200, thunk)

    def _sendChunkAck(self, chunk):
        proto = { "opcode":"CHUNKACK", "chunk":chunk}
        ack = "<<@@@@<<%s<<@@@@<<" % repr(proto)
        thunk = functools.partial(self._sendXferProtoAckCB, ack)
        QTimer.singleShot(200, thunk)
        
    def _sendXferProtoAckCB(self, acktxt):
        if OPT_VERBOSE:
            print("_sendXferProtoAckCB(%r)" % acktxt)
        QApplication.clipboard().setText(acktxt)
        self._lastACK = acktxt
        self._overdueTMR.start(2000)
        
    def _overdueCB(self):
        print("_overdueCB: %s" % self._lastACK)
        self._overdueTMR.stop()
        if self._lastACK:
            self._sendXferProtoAckCB(self._lastACK)
        
    def appendText(self, text):
        self._inputTE.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        self._inputTE.insertPlainText(text+'\n')
        self._inputTE.ensureCursorVisible()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ExampleWindow()
    print
    mainWin.show()
    sys.exit(app.exec_())

