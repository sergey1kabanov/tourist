#!/usr/bin/env python
# -*- coding: utf-8 -*


from socketIO_client import SocketIO

import logging
import websocket
import thread
import time
import json
import ast
import threading
import sys
import json
from PyQt4 import QtGui

from gui import ChatWidget
from message import Message

LOGIN_LENGTH = 15

def login_string(login):
    if LOGIN_LENGTH < len(login):
        return login[:LOGIN_LENGTH]
    else:
        return login



def on_message(ws, message):
    #m = json.loads(message[1:][0])
    j = json.loads(message)
    mtype = j['type']

    if mtype == 'welcome':
        auth = {
                   'type': 'auth', 
                   'data': 
                    {
                        'user_id': 0, 
                        'token': ''
                    }
               }

        answer = json.dumps(auth)
        ws.send(answer)
    elif mtype == 'success_auth':
        #print j
        join_answer = json.dumps({'type': 'join', 'data': {
            #'channel_id': 1999, #My
            #'channel_id': 1717, #Vicarion
            'channel_id': ws.settings['channel_id'], #Happa_
            'hidden': '',
            'mobile': False
        }})
        ws.send(join_answer)
    elif mtype == 'message':
        data = j['data']
        print data
        ws.window.print_message(Message(data['user_name'], data['text'], 'goodgame'))
    else:
        print j

def on_error(ws, error):
    print 'Error occurred: %s' % repr(error)

def on_close(ws):
    print '### closed ###'


def run_app(ws):
    while True:
        ws.run_forever()


class GoodgameChat(websocket.WebSocketApp):
    def __init__(self, settings):
        self.settings = settings
        websocket.WebSocketApp.__init__(self, 'ws://goodgame.ru:8080/chat/websocket',
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
        self.window = ChatWidget(settings)
        self.window.show()
    
    def start(self):
        t = threading.Thread(target=run_app, args=[self])
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    try:
        with open('conf.json', 'r') as f:
            settings = json.load(f)
    except:
        settings = {'channel_id': 2059, 'login': 'Happa_'}        

    app = QtGui.QApplication(sys.argv)
    w = ChatWidget(settings)
    chat = GoodgameChat(settings)
    chat.start()
    
    sys.exit(app.exec_())
