#coding=utf-8
#!/usr/bin/python
# board.py

import shape
import tetrominoes
from PyQt4 import QtCore, QtGui

class Board(QtGui.QFrame):
    BoardWidth = 10
    BoardHeight = 22
    Speed = 500

    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent)
        self.timer = QtCore.QBasicTimer()
        self.isWaitingAfterLine = False
        self.curPiece = shape.Shape()
        self.nextPiece = shape.Shape()
        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()
        self.nextPiece.setRandomShape()

    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape

    def squareWidth(self):
        return self.contentsRect().width() / Board.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() / Board.BoardHeight

    def start(self):
        if self.isPaused:
            return
        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard()
        self.emit(QtCore.SIGNAL("messageToStatusbar(QString)"),
                  str(self.numLinesRemoved))
        self.newPiece()
        self.timer.start(Board.Speed, self)

    def pause(self):
        if not self.isStarted:
            return
        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.emit(QtCore.SIGNAL("messageToStatusbar(QString)"), "paused")
        else:
            self.timer.start(Board.Speed, self)
            self.emit(QtCore.SIGNAL("messageToStatusbar(QString)"),
                      str(self.numLinesRemoved))
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        rect = self.contentsRect()
        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()

        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)

                if shape != tetrominoes.Tetrominoes.NoShape:
                    self.drawSquare(painter,
                                    rect.left() + j * self.squareWidth(),
                                    boardTop + i * self.squareHeight(), shape)

        if self.curPiece.shape() != tetrominoes.Tetrominoes.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)

                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                                boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                                self.curPiece.shape())

    def keyPressEvent(self, event):
        if not self.isStarted or self.curPiece.shape() == tetrominoes.Tetrominoes.NoShape:
            QtGui.QWidget.keyPressEvent(self, event)
            return

        key = event.key()

        if key == QtCore.Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == QtCore.Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == QtCore.Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == QtCore.Qt.Key_Down:
            self.tryMove(self.curPiece.rotatedRight(), self.curX, self.curY)

        elif key == QtCore.Qt.Key_Up:
            self.tryMove(self.curPiece.rotatedLeft(), self.curX, self.curY)


        elif key == QtCore.Qt.Key_Space:
            self.dropDown()

        elif key == QtCore.Qt.Key_D:
            self.oneLineDown()

        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()
        else:
            QtGui.QFrame.timerEvent(self, event)

    def clearBoard(self):
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(tetrominoes.Tetrominoes.NoShape)

    def dropDown(self):
        newY = self.curY
        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1
        self.pieceDropped()

    def oneLineDown(self):
        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def pieceDropped(self):
        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())
        self.removeFullLines()
        if not self.isWaitingAfterLine:
            self.newPiece()

    def removeFullLines(self):
        numFullLines = 0
        rowsToRemove = []

        for i in range(Board.BoardHeight):
            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == tetrominoes.Tetrominoes.NoShape:
                    n = n + 1
            if n == 10:
                rowsToRemove.append(i)
        rowsToRemove.reverse()

        for m in rowsToRemove:
            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))
        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.emit(QtCore.SIGNAL("messageToStatusbar(QString)"),
                      str(self.numLinesRemoved))
            self.isWaitingAfterLine = True
            self.curPiece.setShape(tetrominoes.Tetrominoes.NoShape)
            self.update()

    def newPiece(self):
        self.curPiece = self.nextPiece
        self.nextPiece.setRandomShape()
        self.curX = Board.BoardWidth / 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()
        if not self.tryMove(self.curPiece, self.curX, self.curY):
            self.curPiece.setShape(tetrominoes.Tetrominoes.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.emit(QtCore.SIGNAL("messageToStatusbar(QString)"), "Game over")

    def tryMove(self, newPiece, newX, newY):
        for i in range(4):
            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)
            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
            if self.shapeAt(x, y) != tetrominoes.Tetrominoes.NoShape:
                return False
        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()
        return True

    def drawSquare(self, painter, x, y, shape):
        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
        color = QtGui.QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2, color)
        painter.setPen(color.light())



        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)
        painter.setPen(color.dark())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)







