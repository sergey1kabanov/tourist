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
from PyQt4 import QtGui

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
        print j
        ws.send(answer)
    elif mtype == 'success_auth':
        #print j
        join_answer = json.dumps({'type': 'join', 'data': {
            'channel_id': 1999,#1717 Vicarion, #2059 Happa_,
            'hidden': '',
            'mobile': False
        }})
        #print join_answer
        print j
        ws.send(join_answer)
    elif mtype == 'message':
        #print j
        data = j['data']
        print data
        w.append('<span style="font-size:8pt; font-weight:600; color:#0000aa;">%s:</span>: %s'\
                                         % (login_string(data['user_name']), data['text']))
    #else:
    #    print j

def on_error(ws, error):
    print 'Error occurred: %s' % repr(error)

def on_close(ws):
    print '### closed ###'


def run_app(ws):
    while True:
        ws.run_forever()

if __name__ == '__main__':
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QTextEdit()
    ws = websocket.WebSocketApp("ws://goodgame.ru:8080/chat/websocket",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    #ws.enableTrace(True)
    ws.window = w
    t = threading.Thread(target=run_app, args=[ws])
    t.setDaemon(True)
    t.start()
    
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())
