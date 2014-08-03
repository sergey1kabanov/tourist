# -*- coding: utf-8

from PyQt4 import QtGui
from PyQt4 import QtCore
from message import Message
from smiles import get_image
import re
import sys

MAX_LOGIN_SIZE = 12

DARK_BLUE = QtGui.QColor(24, 24, 39)
LIGHT_BLUE = QtGui.QColor(115, 173, 255)
WHITE = QtGui.QColor(174, 193, 209)

LOGIN_FORMAT = QtGui.QTextCharFormat()
LOGIN_FORMAT.setFont(QtGui.QFont('Courier', 11))
LOGIN_FORMAT.setForeground(QtGui.QBrush(LIGHT_BLUE))

TEXT_FORMAT = QtGui.QTextCharFormat()
TEXT_FORMAT.setFont(QtGui.QFont('Arial', 11))
TEXT_FORMAT.setForeground(QtGui.QBrush(WHITE))

class ChatWidget(QtGui.QTextEdit):
    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Base, DARK_BLUE)
        self.setPalette(palette)
        self.cursor = self.cursorForPosition(QtCore.QPoint(0, 0))

    def adjust_login_size(self, login):
        login_size = len(login)
        if login_size < MAX_LOGIN_SIZE:
            login = login + ' ' * (MAX_LOGIN_SIZE - login_size)

        return login + ' '

    def print_message(self, message):
        self.cursor.insertText(self.adjust_login_size(message.login), LOGIN_FORMAT)
        self.print_message_text(message.text, message.chat)
        #self.cursor.insertText(message.text + '\n', TEXT_FORMAT)

    def print_message_text(self, text, chat):
        current_idx = 0

        while True:

            mo = re.search(r':([a-z,A-Z,0-9]+):', text[current_idx:])

            if mo == None:
                self.cursor.insertText(text[current_idx:] + '\n', TEXT_FORMAT)
                return

            code = mo.groups(1)[0]

            try:
                image = get_image(':' + code + ':', chat)
                self.cursor.insertText(text[current_idx:mo.start()], TEXT_FORMAT)
                self.cursor.insertImage(image)
                current_idx =  current_idx + mo.end()
            except Exception as e:
                self.cursor.insertText(text[current_idx:(mo.end() - 1)], TEXT_FORMAT)
                current_idx = current_idx + (mo.end() - 1)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')

    text_edit = ChatWidget(w)

    text_edit.print_message(Message('ComixZone3', 'Hello!', 'goodgame'))

    text_edit.print_message(Message('mess', 'Hello!', 'goodgame'))

    text_edit.print_message(Message('messalina123', 'Hello!', 'goodgame'))

    text_edit.print_message(Message('messalina123', 't :peka123peka:peka:', 'goodgame'))

    w.show()

    sys.exit(app.exec_())

