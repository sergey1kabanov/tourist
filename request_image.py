#!/usr/bin/env python

import httplib 
import urllib
import sys
try:
    import simplejson as json
except:
    import json

TOKEN = '2ed0f94dd7824bfa8136513a067eb337'

def upload_image_yandex(image):
    headers = {'Content-type': 'image/jpeg', 'Accept': 'application/json', 'Authorization': 'OAuth %s' % TOKEN }
    conn = httplib.HTTPConnection('api-fotki.yandex.ru')
    conn.request('POST', '/api/users/sergey1kabanov/album/367938/photos/', image, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    try:
        return json.loads(data)['img']['XL']['href']
    except:
        raise Exception('Bad response from api-fotki.yandex.ru: %s' % data)

def upload_image_custom(image):
    address = 'arma-granit.ru'
    conn = httplib.HTTPSConnection(address, 54321, './file_server/cert/client/client.key', './file_server/cert/client/client.pem')
    conn.request('POST', '/upload', 'trololo')
    filename = conn.getresponse().read()
    conn.close()
    return 'http://%s:54322%s' % (address, filename)

def search_by_image(image):
    url = upload_image_custom(image)
    print url
    conn = httplib.HTTPConnection('images.google.com')
    conn.request('GET', '/searchbyimage?image_url=%s' % url)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    if response.status != 302:
        raise 'Bad response from images.google.com: %s' % data

    start = data.find('A HREF="') + len('A HREF="')
    finish = data.find('"', start)
    redirect_url = data[start:finish]
    '''
    start = redirect_url.find('http://') + len('http://')
    finish = redirect_url.find('/', start)
    server = redirect_url[start:finish]
    path = redirect_url[finish:]

    print server, path
    
    headers = {'Accept': 'application/json'}
    conn = httplib.HTTPConnection(server)
    conn.request('GET', path, '', headers)
    response = conn.getresponse()
    return response.read()
    '''

    return redirect_url
