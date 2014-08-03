from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')

    text_edit = QtGui.QTextEdit(w)

    cursor = text_edit.cursorForPosition(QtCore.QPoint(0, 0))

    #cursor.clearSelection()
    #cursor.movePosition(QtGui.QTextCursor.NextWord, QtGui.QTextCursor.KeepAnchor)

    my_format = QtGui.QTextCharFormat()

    my_format.setFont(QtGui.QFont(("Helvetica", 12, QtGui.QFont.Bold)))

    text_edit.setCurrentCharFormat(my_format)

    cursor.insertText('<span style="font-size:8pt; font-weight:600; color:#0000aa;">Hello World</span>: %s')
    cursor.insertText("Hello World")

    w.show()

    sys.exit(app.exec_())