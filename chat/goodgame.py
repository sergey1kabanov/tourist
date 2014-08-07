import websocket
import threading
import time
import logging
import json
from PyQt4 import QtGui

from message import Message

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
        ws.chat_widget.print_message(Message(data['user_name'], data['text'], 'goodgame'))
    else:
        print j

def on_error(ws, error):
    print 'Error occurred: %s' % repr(error)

def on_close(ws):
    print '### closed ###'


class GoodgameChat(websocket.WebSocketApp):
    def __init__(self, settings, chat_widget):
        self.settings = settings
        websocket.WebSocketApp.__init__(self, 'ws://goodgame.ru:8080/chat/websocket',
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
        self.chat_widget = chat_widget


    def run(self):
        while True:
            self.run_forever()
            time.sleep(5)
   

    def start(self):
        t = threading.Thread(target=self.run)
        t.setDaemon(True)
        t.start()

