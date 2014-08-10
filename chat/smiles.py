import tinycss
import re
import httplib
import urllib2
import json

from PyQt4 import QtGui, QtCore


class TwitchSmiles:
    SMILES_URL = 'http://api.twitch.tv/kraken/chat/emoticons'

    def __init__(self):
        self.smiles = {}
        self.images = {}
        
        try:
            with open('twitch_smiles.json', 'r') as f:
                info = json.load(f)
        except:
            info = json.load(urllib2.urlopen(self.SMILES_URL, timeout=5))
            with open('twitch_smiles.json', 'w') as f:
                json.dump(info, f)

        for e in info['emoticons']:
            for i in e['images']:
                if i['emoticon_set'] is None:
                    self.smiles[e['regex']] = i
                    break

    def get_smile(self, code):
        if not code in self.smiles:
            raise Exception('Smile %s not found' % code)
        image = self.images.get(code, None)
        if not image:
            data = urllib2.urlopen(self.smiles[code]['url'], timeout=5).read()
            image = QtGui.QImage()
            image.loadFromData(data)
            self.images[code] = image

        return image


    def get_all_codes(self):
        return self.smiles.keys()




class SC2TVSmiles:
    CHAT_IMG_DIR = '/img/'

    def __init__(self):
        try:
            with open('sc2tv_smiles.json', 'r') as f:
                smiles = json.load(f)
        except:
            conn = httplib.HTTPConnection('chat.sc2tv.ru')
            conn.request('GET', '/js/smiles.js')
            response = conn.getresponse()
            data = response.read()
            idx_start = data.find('[')
            smiles = json.JSONDecoder().raw_decode(data[idx_start:])[0]
            with open('sc2tv_smiles.json', 'w') as f:
                json.dump(smiles, f)

        self.smiles = {}
        for s in smiles:
            self.smiles[s['code']] = s
        self.images = {}

    def get_url(self, code):
        smile = self.smiles[code]
        return self.CHAT_IMG_DIR + smile['img']
        #'" width="' + smile['width'] +\
        #'" height="' + smile['height'] +\
        #'" class="chat-smile"/>'

    def get_smile(self, code):
        if not code in self.smiles:
            raise Exception('Smile %s not found' % code)
        image = self.images.get(code, None)
        if not image:
            conn = httplib.HTTPConnection('chat.sc2tv.ru')
            conn.request('GET', self.get_url(code))
            data = conn.getresponse().read()
            image = QtGui.QImage()
            image.loadFromData(data)
            self.images[code] = image

        return image


class BackgroundPosition:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str({'x': self.x, 'y': self.y})

class Icon:
    def __init__(self):
        self.bg = None
        self.bg_position = BackgroundPosition(0, 0)
        self.width = None
        self.height = None

    def __str__(self):
        return str({'background': self.bg, 'background-position': self.bg_position, 'width': self.width, 'height': self.height})


def update_icon_by_type(i, types, css):
    itype = '.'.join(types).replace(' ', '')
    for r in css.rules:
        if '#chat#content%s' % itype == r.selector.as_css().replace(' ', ''):
            for d in r.declarations:
                name = d.name
                value = d.value.as_css()
                if name == 'background':
                    mo = re.match(r'url\("?(.*)"?\) no-repeat (-?[0-9]+)p?x? (-?[0-9]+)p?x?', value)
                    if mo:
                        i.bg = mo.group(1)
                        i.bg_position = BackgroundPosition(int(mo.group(2)), -int(mo.group(3)))
                    else:
                        mo = re.match(r'url\("?(.*)"?\)', value)
                        i.bg = mo.group(1)
                elif name == 'background-position':
                    mo = re.match(r'(-?[0-9]+)p?x? (-?[0-9]+)p?x?', value)
                    i.bg_position = BackgroundPosition(int(mo.group(1)), -int(mo.group(2)))
                elif name == 'width':
                    mo = re.match(r'(-?[0-9]+)p?x?', value)
                    i.width = int(mo.group(1))
                elif name == 'height':
                    mo = re.match(r'(-?[0-9]+)p?x?', value)
                    i.height = int(mo.group(1))


def has_type(itype, css):
    for r in css.rules:
        if ('#chat #content img.smiles.%s' % itype) == r.selector.as_css():
            return True
    return False


def get_icon(itemType, css):
    if not has_type(itemType, css):
        raise Exception('No smile')
    i = Icon()
    itemType = '.big .smiles.%s' % itemType
    types = itemType.split('.')
    checked_types = []
    for idx in xrange(0, len(types)):
        checked_types.append(types[idx])
        update_icon_by_type(i, checked_types, css)
    return i


def create_sub_image(image, rect):
    '''
    print rect.x(), rect.y()
    offset = rect.x() * image.depth() / 8 + rect.y() * image.bytesPerLine()
    return QtGui.QImage(image.scanLine(offset), rect.width(), rect.height(),
                  image.bytesPerLine(), image.format())
    '''
    return image.copy(rect)

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
            smile_info = get_icon('%s' % smile_code[1:-1], self.css)
            smiles_img = self.imgs.get(smile_info.bg, None)
            if not smiles_img:
                conn = httplib.HTTPConnection('goodgame.ru')
                conn.request('GET', smile_info.bg)
                response = conn.getresponse()
                smiles_img = QtGui.QImage()
                smiles_img.loadFromData(response.read())
                self.imgs[smile_info.bg] = smiles_img
            
            smile = create_sub_image(smiles_img, QtCore.QRect(smile_info.bg_position.x, smile_info.bg_position.y, 
                                                             smile_info.width, smile_info.height))
            self.smiles[smile_code] = smile
        return smile

goodgame_smiles = SmileStorage()
sc2tv_smiles = SC2TVSmiles()
twitch_smiles = TwitchSmiles()

def get_image(smile_code, chat):
    if chat == 'goodgame':
        return goodgame_smiles.get_smile(smile_code)
    elif chat == 'sc2tv':
        return sc2tv_smiles.get_smile(smile_code)
    elif chat == 'twitch':
        return twitch_smiles.get_smile(smile_code)
    else:
        raise Exception('Chat %s not supported' % chat)

def get_twitch_codes():
    return twitch_smiles.get_all_codes()


if __name__ == '__main__':
    '''
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')

    text_edit = QtGui.QTextEdit(w)

    cursor = text_edit.cursorForPosition(QtCore.QPoint(0, 0))

    cursor.insertImage(get_image(sys.argv[1], 'goodgame'))
    cursor.insertImage(get_image(sys.argv[1], 'goodgame'))

    w.show()

    sys.exit(app.exec_())
    '''
    print twitch_smiles.get_smile('\\:-?\\)')
