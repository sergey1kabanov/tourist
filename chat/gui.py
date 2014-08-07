# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4 import QtCore
from message import Message
from smiles import get_image
import re
import sys
import json

MAX_LOGIN_SIZE = 12

DARK_BLUE = QtGui.QColor(24, 24, 39)
LIGHT_BLUE = QtGui.QColor(115, 173, 255)
WHITE = QtGui.QColor(174, 193, 209)
YELLOW = QtGui.QColor(174, 174, 0) 

LOGIN_FORMAT = QtGui.QTextCharFormat()
LOGIN_FORMAT.setFont(QtGui.QFont('Courier', 11))
LOGIN_FORMAT.setForeground(QtGui.QBrush(LIGHT_BLUE))

TEXT_FORMAT = QtGui.QTextCharFormat()
TEXT_FORMAT.setFont(QtGui.QFont('Arial', 11))
TEXT_FORMAT.setForeground(QtGui.QBrush(WHITE))

TEXT_FORME_FORMAT = QtGui.QTextCharFormat()
TEXT_FORME_FORMAT.setFont(QtGui.QFont('Arial', 11))
TEXT_FORME_FORMAT.setForeground(QtGui.QBrush(YELLOW))

class ChatWidget(QtGui.QTextEdit):
    on_print = QtCore.pyqtSignal(list)

    def __init__(self, settings, parent=None):
        self.settings = settings
        QtGui.QTextEdit.__init__(self, parent)
        self.on_print.connect(self.do_print)
        self.setWindowTitle("CHAT")
        self.resize(400, 500)
        self.setReadOnly(True)
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
        self.on_print.emit([message])

    def do_print(self, message):
        message = message[0]
        self.cursor.insertText(self.adjust_login_size(message.login), LOGIN_FORMAT)
        self.print_message_text(message.text, message.chat)
        self.moveCursor(QtGui.QTextCursor.End)
        self.verticalScrollBar().maximum()

    def print_message_text(self, text, chat):
        current_idx = 0
        
        if chat == 'sc2tv':
            text = re.sub(r'\[b\]([a-z,A-Z,0-9,_,-]+)\[/b\],', lambda mo: '%s,' % mo.group(1), text, count=1)

        text_format = TEXT_FORMAT
        if text.startswith('%s,' % self.settings[chat]['login']):
            text_format = TEXT_FORME_FORMAT
        else:
            text_format = TEXT_FORMAT

        while True:

            if chat == 'goodgame':
                regex = r':([a-z,A-Z,0-9]+):'
            elif chat == 'sc2tv':
                regex = r':s:([a-z,A-Z,0-9]+):'

            mo = re.search(regex, text[current_idx:])

            if mo == None:
                self.cursor.insertText(text[current_idx:] + '\n', text_format)
                return

            code = mo.group(1)

            try:
                image = get_image(':' + code + ':', chat)
                self.cursor.insertText(text[current_idx:mo.start()], text_format)
                self.cursor.insertImage(image)
                current_idx =  current_idx + mo.end()
            except Exception as e:
                self.cursor.insertText(text[current_idx:(mo.end() - 1)], text_format)
                current_idx = current_idx + (mo.end() - 1)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    with open('settings.json') as f:
        settings = json.load(f)
    text_edit = ChatWidget(settings)
    '''
    text_edit.print_message(Message('ComixZone3', 'Hello!', 'goodgame'))

    text_edit.print_message(Message('mess', 'Hello!', 'goodgame'))


    text_edit.print_message(Message('messalina123', 'Hello!', 'goodgame'))

    text_edit.print_message(Message('messalina123', 't :peka123peka:peka:', 'goodgame'))
    '''
    text_edit.print_message(Message('aids', u'\u0427\u0435\u0440\u0435\u043f\u0430\u0448\u043a\u0438 \u043d\u0438\u043d\u0434\u0437\u044f \u043b\u0443\u0447\u0448\u0435 \u0425\u0421 :s:lucky:', 'sc2tv'))
    text_edit.show()

    sys.exit(app.exec_())

