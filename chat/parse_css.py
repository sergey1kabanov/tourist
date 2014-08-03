import tinycss
import re
import sys
import httplib

from PIL import Image
from StringIO import StringIO

class BackgroundPosition:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str({'x': self.x, 'y': self.y})

class Icon:
    def __init__(self):
        self.bg = None
        self.bg_position = None
        self.width = None
        self.height = None

    def __str__(self):
        return str({'background': self.bg, 'background-position': self.bg_position, 'width': self.width, 'height': self.height})


def updateIconByType(i, types, css):
    itype = '.'.join(types)
    for r in css.rules:
        if '#chat #content %s' % itype == r.selector.as_css():
            for d in r.declarations:
                name = d.name
                value = d.value.as_css()
                if name == 'background':
                    mo = re.match(r'url\("?(.*)"?\)', value)
                    i.bg = mo.group(1)
                elif name == 'background-position':
                    mo = re.match(r'(-?[0-9]+)p?x? (-?[0-9]+)p?x?', value)
                    i.bg_position = BackgroundPosition(mo.group(1), mo.group(2))
                elif name == 'width':
                    i.width = value
                elif name == 'height':
                    i.height = value


def get_icon(itemType, css):
    i = Icon()
    types = itemType.split('.')
    checked_types = []
    for idx in xrange(0, len(types)):
        checked_types.append(types[idx])
        updateIconByType(i, checked_types, css)
    return i 


class SmileStorage:
    def __init__(self):
        conn = httplib.HTTPConnection('goodgame.ru')
        conn.request('GET', '/css/compiled/chat.css')
        response = conn.getresponse()
        parser = tinycss.make_parser('page3')
        self.css = parser.parse_stylesheet(response.read())

        self.smiles = {}
        self.imgs = {}


    def get_smile(self, smile_code):
        smile = self.smiles.get(smile_code, None)
        if not smile:
            smile_info = get_icon('img.smiles.%s' % smile_code[1:-1], self.css)
            smiles_img = self.imgs.get(smile_info.bg, None)
            if not smiles_img:
                conn = httplib.HTTPConnection('goodgame.ru')
                conn.request('GET', smile_info.bg)
                response = conn.getresponse()
                f = StringIO(response.read())
                smiles_img = Image.open(f)
                self.imgs[smile_info.bg] = smiles_img
            smile = smile_info
            self.smiles[smile_code] = smile
        return smile


if __name__ == '__main__':
    ss = SmileStorage()
    print ss.get_smile(sys.argv[1])
    print ss.get_smile(sys.argv[1])
