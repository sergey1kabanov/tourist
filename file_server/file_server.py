#!/usr/bin/env python

import os
import sys
import logging
import BaseHTTPServer
import threading
import httplib
import json
import ssl
import uuid

class ExecutionHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    @classmethod
    def init(cls, conf):
        cls.conf = conf
        cls.url_prefix = conf['url_prefix']
        cls.image_folder = conf['image_folder']
        cls.max_count = conf['max_count']
        if not os.path.exists(cls.image_folder):
            os.makedirs(cls.image_folder)

        cls.files = os.listdir(cls.image_folder)
        

    def reply_file(self, path):
        try:
            with open(os.path.join(self.image_folder, path)) as f:
                self.wfile.write(f.read())
        except:
            self.send_error(404)
            
    def clear(self):
        while len(self.files) >= self.max_count:
            rm_file = self.files.pop(0)
            logging.info('Clearing: remove old file %s' % rm_file)
            os.remove(os.path.join(self.image_folder, rm_file))

    def do_GET(self):
        prefix_pos = self.path.find(self.url_prefix)
        if prefix_pos == 0:
            self.reply_file(self.path[len(self.url_prefix):])
            return
        
        self.send_error(404)

    def do_POST(self):
        if self.path != '/upload':
            self.send_error(404)
            return

        try:
            length = int(self.headers.getheader('content-length'))
            if not length:
                self.send_error(400)

            self.clear()
            data = self.rfile.read(length)
            new_name = uuid.uuid1().hex
            logging.info('Add new file %s' % new_name)
            with open(os.path.join(self.image_folder, new_name), 'w') as f:
                f.write(data)
            self.files.append(new_name)
            self.wfile.write(self.url_prefix + new_name)
        except Exception as error:
            self.send_error(400)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

    conf_file = sys.argv[1]
    conf = json.load(open(conf_file, 'r'))
    ExecutionHandler.init(conf)

    server_class = BaseHTTPServer.HTTPServer

    httpd = server_class(('', int(conf['port'])), ExecutionHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, 
                                   certfile=conf['server_cert'], 
                                   server_side=True,
                                   cert_reqs=ssl.CERT_REQUIRED,
                                   ca_certs=conf['auth_cert'])
    logging.info('Server Starts - %s:%s' % ('', conf['port']))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
         pass
    httpd.server_close()
    logging.info('Server Stops - %s:%s' % ('', conf['port']))



