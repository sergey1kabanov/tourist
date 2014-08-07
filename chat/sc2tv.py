import json
import httplib
import time
import traceback
import threading

from message import Message

def beautify_json(json_value):
    return json.dumps(json_value, sort_keys=True, indent=4)

def bprint(j):
    print beautify_json(j)


class SC2TVChat:
    def __init__(self, settings, chat_widget):
        self.settings = settings
        self.url = 'chat.sc2tv.ru'
        self.channelId = 160487
        self.chat_widget = chat_widget

    def run(self):
        last_id = 0
        while True:
            try:
                conn = httplib.HTTPConnection(self.url)
                conn.request('GET', '/memfs/channel-%s.json' % self.channelId)
                response = conn.getresponse()
                data = response.read()
                if not data:
                    continue
                try:
                    j = json.loads(data)
                except:
                    continue
                if not 'messages' in j:
                    continue
                j = j['messages']
                if not j:
                    continue
                for m in reversed(j):
                    if m['id'] <= last_id:
                        continue
                    print m
                    self.chat_widget.print_message(Message(m['name'], m['message'], 'sc2tv'))
                last_id = j[0]['id']
            except Exception:
                print traceback.format_exc()
            finally:
                time.sleep(5)


    def start(self):
        t = threading.Thread(target=self.run)
        t.setDaemon(True)
        t.start()

