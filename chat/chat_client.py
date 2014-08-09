import threading

from message import Message

class ChatClient:
    CHAT_NAME = None

    def __init__(self, settings, chat_widget):
        self.settings = settings
        self.chat_widget = chat_widget

    def run(self):
        raise Exception('Not implemented')

    def start(self):
        t = threading.Thread(target=self.run)
        t.setDaemon(True)
        t.start()

    def print_message(self, login, text):
        self.chat_widget.print_message(Message(login, text, self.CHAT_NAME))
