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
        with open('settings.json', 'r') as f:
            settings = json.load(f)
    except:
        settings = {
                        'goodgame': 
                        {
                            'login': 'Happa_', 
                            'channel_id': 2059
                        },
                        'sc2tv':
                        {
                            'login': 'Happa',
                            'channel_id': 160487 
                        }
                   }

    app = QtGui.QApplication(sys.argv)
    w = ChatWidget(settings)
    w.show()
 
    gg_chat = GoodgameChat(settings['goodgame'], w)
    sc2tv_chat = SC2TVChat(settings['sc2tv'], w)
    for chat in [gg_chat, sc2tv_chat]:
        chat.start()
    
    sys.exit(app.exec_())
