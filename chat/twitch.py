import socket
import irc.client
import traceback
import time

from chat_client import ChatClient


class TwitchChat(ChatClient):
    CHAT_NAME = 'twitch'
    ICON_URL = 'http://twitch.tv/favicon.ico'

    def __init__(self, settings, chat_widget):
        ChatClient.__init__(self, settings, chat_widget)
        self.settings = settings
        self.url = 'irc.twitch.tv'
        self.port = 6667
        self.addr = None


    def run(self):
        last_id = 0
        while True:
            try:
                _, _, addrs = socket.gethostbyname_ex(self.url)
                for a in addrs:
                    try:
                        print 'Try to connect to %s:%s' % (a, self.port)
                        socket.create_connection((a, self.port), 1)
                        self.addr = a
                    except:
                        pass

                if not self.addr:
                    raise Exception('All servers do not respond')

                client = irc.client.IRC()
                c = client.server().connect(self.addr, self.port, self.settings['login'], password=self.settings['authtoken'])
                c.add_global_handler('welcome', self.on_connect)
                c.add_global_handler('pubmsg', self.on_message)
                client.process_forever()

            except Exception:
                print traceback.format_exc()
            finally:
                time.sleep(5)

    def on_connect(self, connection, event):
        channel = '#' + self.settings['channel']
        if not irc.client.is_channel(channel):
            raise Exception('%s is not irc channel' % channel)
        connection.join(channel)


    def on_message(self, connection, event):
        login = event.source.split('!')[0]
        text = event.arguments[0]
        print '%s: %s' % (login, text)
        self.print_message(login, text)



def main():
    pass

if __name__ == '__main__':
    main()
