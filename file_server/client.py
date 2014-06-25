#!/usr/bin/env python

import httplib


conn = httplib.HTTPSConnection('127.0.0.1', 54321, './cert/client/client.key', './cert/client/client.pem')
conn.request('POST', '/upload', 'trololo')
filename = conn.getresponse().read()
conn.close()

print filename
 

conn = httplib.HTTPSConnection('127.0.0.1', 54321, './cert/client/client.key', './cert/client/client.pem')
conn.request('GET', filename)
result = conn.getresponse().read()
conn.close()
        
print result
