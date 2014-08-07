#!/usr/bin/env python
# -*- coding: utf-8 -*

import logging
import thread
import time
import json
import ast
import sys
from PyQt4 import QtGui

from gui import ChatWidget
from sc2tv import SC2TVChat
from goodgame import GoodgameChat


if __name__ == '__main__':
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    try:
        with open('conf.json', 'r') as f:
            settings = json.load(f)
    except:
        settings = {'channel_id': 2059, 'gg_login': 'Happa_', 'sc2tv_login': 'Happa'}

    app = QtGui.QApplication(sys.argv)
    w = ChatWidget(settings)
    w.show()
 
    gg_chat = GoodgameChat(settings, w)
    sc2tv_chat = SC2TVChat(settings, w)
    for chat in [gg_chat, sc2tv_chat]:
        chat.start()
    
    sys.exit(app.exec_())
