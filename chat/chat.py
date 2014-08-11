#!/usr/bin/env python
# -*- coding: utf-8 -*

import logging
import json
import sys
from PyQt4 import QtGui

from gui import ChatWidget
from sc2tv import SC2TVChat
from goodgame import GoodgameChat
from twitch import TwitchChat

import sys

if __name__ == '__main__':
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    if len(sys.argv) > 1:
        settings_file = sys.argv[1]
    else:
        settings_file = 'settings.json'
    with open(settings_file, 'r') as f:
        settings = json.load(f)

    app = QtGui.QApplication(sys.argv)
    w = ChatWidget(settings)
    w.show()
 
    chats = [
                GoodgameChat(settings['goodgame'], w),
                SC2TVChat(settings['sc2tv'], w),
                TwitchChat(settings['twitch'], w)
    ]
    map(lambda chat: chat.start(), chats)

    sys.exit(app.exec_())
