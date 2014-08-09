import json
import httplib
import time
import traceback

from chat_client import ChatClient


def beautify_json(json_value):
    return json.dumps(json_value, sort_keys=True, indent=4)


def bprint(j):
    print beautify_json(j)


class SC2TVChat(ChatClient):
    CHAT_NAME = 'sc2tv'
    ICON_URL = 'http://sc2tv.ru/favicon.ico'

    def __init__(self, settings, chat_widget):
        ChatClient.__init__(self, settings, chat_widget)
        self.settings = settings
        self.url = 'chat.sc2tv.ru'


    def run(self):
        last_id = 0
        while True:
            try:
                conn = httplib.HTTPConnection(self.url)
                conn.request('GET', '/memfs/channel-%s.json' % self.settings['channel_id'])
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
                    self.print_message(m['name'], m['message'])
                last_id = j[0]['id']
            except Exception:
                print traceback.format_exc()
            finally:
                time.sleep(5)
