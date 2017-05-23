#coding=utf-8
#!/usr/bin/python
# tetris.py

import board
from PyQt4 import QtCore, QtGui


class Tetris(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setGeometry(300, 300, 180, 380)
        self.setWindowTitle('Tetris')
        self.tetrisboard = board.Board(self)
        self.setCentralWidget(self.tetrisboard)
        self.statusbar = self.statusBar()
        self.connect(self.tetrisboard, QtCore.SIGNAL("messageToStatusbar(QString)"),
                     self.statusbar, QtCore.SLOT("showMessage(QString)"))
        self.tetrisboard.start()
        self.center()
        #sys.exit(app.exec_())

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)


