#!/usr/bin/env python

import httplib 
import urllib
import sys
try:
    import simplejson as json
except:
    import json

TOKEN = '2ed0f94dd7824bfa8136513a067eb337'

def upload_image(image):
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

def search_by_image(image):
    url = upload_image(image)
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

#    return urllib.urlopen(redirect_url).read()

image = open(sys.argv[1], 'r').read()
print search_by_image(image)
