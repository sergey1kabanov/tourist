# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4 import QtCore
from message import Message
from smiles import SmileStorage
import re
import sys
import json
import urllib2
import webbrowser

MAX_LOGIN_SIZE = 15

DARK_BLUE = QtGui.QColor(24, 24, 39)
LIGHT_BLUE = QtGui.QColor(115, 173, 255)
WHITE = QtGui.QColor(174, 193, 209)
YELLOW = QtGui.QColor(0xf1, 0xbd, 0x13) 

LOGIN_FORMAT = QtGui.QTextCharFormat()
LOGIN_FORMAT.setFont(QtGui.QFont('Courier', 11))
LOGIN_FORMAT.setForeground(QtGui.QBrush(LIGHT_BLUE))

TEXT_FORMAT = QtGui.QTextCharFormat()
TEXT_FORMAT.setFont(QtGui.QFont('Arial', 11))
TEXT_FORMAT.setForeground(QtGui.QBrush(WHITE))

TEXT_HILIGHTED_FORMAT = QtGui.QTextCharFormat()
TEXT_HILIGHTED_FORMAT.setFont(QtGui.QFont('Arial', 11))
TEXT_HILIGHTED_FORMAT.setForeground(QtGui.QBrush(YELLOW))

class ChatWidget(QtGui.QTextBrowser):
    on_print = QtCore.pyqtSignal(list)

    def __init__(self, settings, parent=None):
        self.settings = settings
        QtGui.QTextBrowser.__init__(self, parent)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.open_url)
        self.on_print.connect(self.do_print)
        self.setWindowTitle("CHAT")
        self.resize(400, 500)
        self.setReadOnly(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Base, DARK_BLUE)
        self.setPalette(palette)
        self.cursor = self.cursorForPosition(QtCore.QPoint(0, 0))
        blockFormat = self.cursor.blockFormat()
        blockFormat.setTopMargin(10)
        self.cursor.setBlockFormat(blockFormat)
        self.smile_storage = SmileStorage(settings)

    def open_url(self, url):
        QtGui.QDesktopServices.openUrl(url)

    def adjust_login_size(self, login):
        login_size = len(login)
        if login_size < MAX_LOGIN_SIZE:
            login = login + ' ' * (MAX_LOGIN_SIZE - login_size)
        if login_size > MAX_LOGIN_SIZE:
            login = login[0: MAX_LOGIN_SIZE-3] + '...'

        return ' ' + login + ' '

    def print_message(self, message):
        self.on_print.emit([message])

    def do_print(self, message):
        message = message[0]
        if message.icon:
            self.cursor.insertImage(message.icon)
        self.cursor.insertText(self.adjust_login_size(message.login), LOGIN_FORMAT)
        #self.cursor.insertHtml('')
        self.print_message_text(message.text, message.chat)
        self.moveCursor(QtGui.QTextCursor.End)
        self.verticalScrollBar().maximum()

    def print_message_text_twitch(self, text, chat):
        text_format = self.get_message_text_format(text, chat)
        twitch_codes = self.smile_storage.get_twitch_codes()

        smile_indexes = []
        for regex in twitch_codes:
            current_idx = 0
            while True:
                mo = None

                if regex:
                    mo = re.search(regex, text[current_idx:])

                if mo is None:
                    break

                smile_indexes.append((current_idx + mo.start(), current_idx + mo.end(), regex, 'SMILE'))
                current_idx =  current_idx + mo.end()

        url_regexp = ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
        current_idx = 0
        while True:
            mo = None

            if url_regexp:
                mo = re.search(url_regexp, text[current_idx:])

            if mo is None:
                break

            smile_indexes.append((current_idx + mo.start(), current_idx + mo.end(), mo.string[mo.start(): mo.end()], 'URL'))
            current_idx =  current_idx + mo.end()


        smile_indexes = sorted(smile_indexes, cmp=lambda p1, p2: cmp(p1[0], p2[0]))

        current_idx = 0
        for smile_index in smile_indexes:
            if smile_index[3] == 'SMILE':
                self.cursor.insertText(text[current_idx: smile_index[0]], text_format)
                self.cursor.insertImage(self.smile_storage.get_image(smile_index[2], chat))
                current_idx = smile_index[1]
            elif smile_index[3] == 'URL':
                self.cursor.insertText(text[current_idx: smile_index[0]], text_format)
                self.cursor.insertHtml('<a style="color: #73adff; font-size: 18px; font-family: Arial;" href="' + smile_index[2] + '">' + smile_index[2] + "</a>")
                current_idx = smile_index[1]
        self.cursor.insertText(text[current_idx:] + '\n', text_format)
        return

    def print_message_text(self, text, chat):

        if chat == 'twitch':
            self.print_message_text_twitch(text, chat)
            return

        special_chars = {
            '&quot;': '"', 
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>'
        }
        for code, char in special_chars.items():
            text = text.replace(code, char)

        current_idx = 0
        
        if chat == 'sc2tv':
            text = re.sub(u'\[b\]([а-я,А-Я,ё,Ё,a-z,A-Z,0-9,_,-,.,\s]+?)\[/b\],', lambda mo: '%s,' % mo.group(1), text, count=1)

        text_format = self.get_message_text_format(text, chat)

        while True:
            regex = None
            mo = None

            if chat == 'goodgame':
                regex = r':([a-z,A-Z,0-9]+?):|<a.*?href="(.*?)">.*?</a>'
            elif chat == 'sc2tv':
                regex = r':s:([a-z,A-Z,0-9]+?):|\[url\](.*?)\[/url\]'

            if regex:
                mo = re.search(regex, text[current_idx:])

            if mo == None:
                self.cursor.insertText(text[current_idx:] + '\n', text_format)
                return

            if mo.group(1) is not None:
                code = mo.group(1)
                try:
                    image = self.smile_storage.get_image(':' + code + ':', chat)
                    self.cursor.insertText(text[current_idx: current_idx + mo.start()], text_format)
                    self.cursor.insertImage(image)
                    current_idx = current_idx + mo.end()
                except Exception as e:
                    self.cursor.insertText(text[current_idx: (current_idx + mo.end() - 1)], text_format)
                    current_idx = current_idx + (mo.end() - 1)

            elif mo.group(2) is not None:
                code = mo.group(2)
                self.cursor.insertText(text[current_idx: current_idx + mo.start()], text_format)
                self.cursor.insertHtml('<a style="color: #73adff; font-size: 18px; font-family: Arial;" href="' + code + '">' + code + "</a>")
                current_idx = current_idx + mo.end()

    def get_message_text_format(self, text, chat):
        if text.startswith('%s,' % self.settings[chat]['login']):
            return TEXT_HILIGHTED_FORMAT
        else:
            return TEXT_FORMAT

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    with open('settings.json') as f:
        settings = json.load(f)
    text_edit = ChatWidget(settings)

    GG_ICON_URL = 'http://goodgame.ru/favicon.ico'

    gg_icon = QtGui.QImage()
    gg_icon.loadFromData(urllib2.urlopen(GG_ICON_URL, timeout=3).read())

    TW_ICON_URL = 'http://twitch.tv/favicon.ico'

    tw_icon = QtGui.QImage()
    tw_icon.loadFromData(urllib2.urlopen(TW_ICON_URL, timeout=3).read())

    SC_ICON_URL = 'http://sc2tv.ru/favicon.ico'

    sc_icon = QtGui.QImage()
    sc_icon.loadFromData(urllib2.urlopen(SC_ICON_URL, timeout=3).read())

    #text_edit.print_message(Message('aids', u'\u0427\u0435\u0440\u0435\u043f\u0430\u0448\u043a\u0438 \u043d\u0438\u043d\u0434\u0437\u044f \u043b\u0443\u0447\u0448\u0435 \u0425\u0421 :s:lucky:', 'sc2tv'))
    #text_edit.print_message(Message('aids', u'\u0427\u0435\u0440\u0435\u043f\u0430\u0448\u043a\u0438 \u043d\u0438\u043d\u0434\u0437\u044f \u043b\u0443\u0447\u0448\u0435 \u0425\u0421 :s:lucky:', 'goodgame'))
    #text_edit.print_message(Message('aids12345678901234567890', 'trololo :gg: tololo :gg: tololo', 'goodgame', gg_icon))
    #text_edit.print_message(Message('thegodis', 'trololo :gg:', 'goodgame', gg_icon))
    #text_edit.print_message(Message('Kapibara', 'trololo :gg:', 'goodgame', gg_icon))

    text_edit.print_message(Message('thegodis', 'goodgame.ru www.goodgame.ru', 'twitch', tw_icon))
    text_edit.print_message(Message('thegodis', 'http://goodgame.ru', 'twitch', tw_icon))
    text_edit.print_message(Message('gg', 'a:gg:<a href="http://goodg:gg:ame.ru">http://goodgame.ru</a>  a:gg:', 'goodgame', gg_icon))
    text_edit.print_message(Message('afafsfagag', ':s:peka:[url]http://sc2tv.ru[/url] http://sc2tv.ru', 'sc2tv', sc_icon))

    #text_edit.print_message(Message('aids', 'trololo :gg:', 'goodgame', sc_icon))
    text_edit.show()

    sys.exit(app.exec_())

