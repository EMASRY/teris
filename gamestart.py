#coding=utf-8
#!/usr/bin/python
# gamestart.py

import sys
import tetris
from PyQt4 import  QtGui

app = QtGui.QApplication(sys.argv)
tetris = tetris.Tetris()
tetris.show()
sys.exit(app.exec_())