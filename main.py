import webbrowser

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
#from kivy.uix.camera import Camera
from camera import TouristCamera
from kivy.core.image import Image
from PIL import Image as PilImage
from StringIO import StringIO

from request_image import search_by_image

class MyApp(App):

    def on_image(self, *args):
        if not self.camera.texture:
            return
        url = search_by_image(self.camera.get_picture())
        webbrowser.open(url)
#        f = open('3.png', 'w')
#        f.write(data.getvalue())
#        f.close()

    def build(self):
        l1 = BoxLayout(orientation='vertical')
        l2 = BoxLayout(orientation='horizontal', size_hint=(1,.1))
        self.camera = TouristCamera(resolution=(640, 480))
        self.camera.camera_id = 0
        self.camera.play=True
#        l1.add_widget(Label(text='Trololo'))
        l1.add_widget(self.camera)
        b = Button(text='Pic')
        b.bind(on_press=self.on_image)
        l2.add_widget(b)
        l2.add_widget(Button(text='Search'))
        l1.add_widget(l2)
        return l1

if __name__ == '__main__':
    MyApp().run()
