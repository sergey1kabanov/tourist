import tinycss
import re
import sys
import httplib

from PyQt4 import QtGui, QtCore
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


def update_icon_by_type(i, types, css):
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
                    i.bg_position = BackgroundPosition(int(mo.group(1)), -int(mo.group(2)))
                elif name == 'width':
                    mo = re.match(r'(-?[0-9]+)p?x?', value)
                    i.width = int(mo.group(1))
                elif name == 'height':
                    mo = re.match(r'(-?[0-9]+)p?x?', value)
                    i.height = int(mo.group(1))


def has_type(itype, css):
    for r in css.rules:
        if '#chat #content %s' % itype == r.selector.as_css():
            return True
    return False


def get_icon(itemType, css):
    if not has_type(itemType, css):
        raise Exception('No smile')
    i = Icon()
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
            smile_info = get_icon('img.smiles.%s' % smile_code[1:-1], self.css)
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

def get_image(smile_code, chat):
    if chat == 'goodgame':
        return goodgame_smiles.get_smile(smile_code)
    else:
        raise Exception('Chat %s not supported' % chat)


if __name__ == '__main__':
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

