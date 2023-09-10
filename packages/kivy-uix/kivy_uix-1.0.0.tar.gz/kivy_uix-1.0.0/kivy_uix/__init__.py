import kivy
import logging
kivy.require('1.9.1') #kivy.require('1.1.3')

from kivy.properties import NumericProperty
import threading
from time import sleep
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.progressbar import ProgressBar
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.clock import Clock
import random
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.graphics import RoundedRectangle, Color, Rectangle
from kivy.metrics import dp
from kivy.uix.slider import Slider
from kivy.core.clipboard import Clipboard

Builder.load_string('''
<MyPopup>:
    size_hint: 0.8, 0.8
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    background_color: 0, 0, 0, 0
    BoxLayout:
        orientation: "vertical"
        padding: dp(5)
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.4, 1
            Rectangle:
                pos: self.pos
                size: self.size
                source: 'fondo2.png'
        BoxLayout:
            orientation: "vertical"
            padding: dp(1)
            Label:
                text: "T&C | About"
                halign: 'center'
                font_size: '25sp'
            Label:
                text: "Type: Gestor de Descarga"
                halign: 'left'
            Label:
                text: "Note: No Consume Megas (MB)"
                halign: 'left'
            Label:
                text: "Mode: Plugin"
                halign: 'left'
            Label:
                text: "Propietario: @raydel0307"
                halign: 'left'
            Label:
                text: "Version: Beta 0.4"
                halign: 'left'
            Label:
                text: "Edicion: c-2021 Compile"
                halign: 'left'
            Label:
                text: "https://t.me/oficial_uploader_rayserver"
                halign: 'left'

<Downloader>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'fondo.png'
    orientation: 'vertical'
    spacing: 10
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.07
        spacing: 20
        padding: [20,0,0,0]
        canvas:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'RayServer DL'
            color: 1, 1, 1, 1
            size_hint_x: 1
            font_size: '25sp'
            bold: True
        Button:
            background_normal: 'about.png'
            size_hint: None, None
            size: self.width, self.width
            height: self.width
            font_size: '10sp'
            on_press: root.emergente()
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.07
        spacing: 5
        padding: [20,0,0,0]
        canvas:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Slider:
            id: slider_value
            orientation: 'horizontal'
            min: 1
            max: 5
            value: 2
            size_hint_x: 1
            step: 1
        Label:
            text: str(slider_value.value)
            color: 1, 1, 1, 1
            font_size: '20sp'
        Button:
            background_normal: 'cancel.png'
            size_hint: None, None
            size: self.width, self.width
            height: self.width
            font_size: '10sp'
            on_press: root.clear_all()
        Button:
            background_normal: 'reestart.png'
            size_hint: None, None
            size: self.width, self.width
            height: self.width
            font_size: '10sp'
            on_press: root.restart()

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.07
        spacing: 5
        padding: [20,0,0,0]
        canvas:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        TextInput:
            id: url_input
            hint_text: 'URL del archivo'
            background_color: (1, 1, 1, 1)
            foreground_color: (0.2, 0.2, 0.2, 1)
            size_hint_x: 0.75
            font_size: '17sp'
            padding: [20, 25, 20, 0]
            halign: 'center'
        Button:
            background_normal: 'paste.png'
            size_hint: None, None
            size: self.width, self.width
            height: self.width
            font_size: '10sp'
            on_press: root.download_file_2()
        Button:
            background_normal: 'ico1.png'
            size_hint: None, None
            size: self.width, self.width
            height: self.width
            font_size: '10sp'
            on_press: root.download_file(url_input.text)
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.76
        spacing: 20
        padding: [20,0,20,0]
        ScrollView:
            GridLayout:
                id: download_list
                cols: 1
                spacing: 20
                size_hint: 1, None
                height: self.minimum_height
                row_default_height: 150
                row_force_default: True
                padding: [0,20,0,20]
<Target>:
    orientation: "horizontal"
    size_hint_y: None
    size_hint_x: 0.8
    height: 200
    filename: ""
    pext: ""
    file_path: ""
    padding: dp(10)
    spacing: 20
    halign: "center"

    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.5
        Rectangle:
            pos: self.pos
            size: self.size

    AsyncImage:
        id: photo_ext
        size_hint_x: 0.2
        source: "other.png"
        keep_ratio: True
        allow_stretch: True

    BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.8
        spacing: dp(20)
        padding: dp(5)

        Label:
            id: label_text
            text: root.filename
            color: 1, 1, 1, 1
            font_size: dp(20)
            halign: "left"
            valign: "middle"

        Label:
            id: label_text_2
            text: "14 MiB de 62 MiB [33%]"
            font_size: dp(15)
            color: 1, 1, 1, 1
''')

class Target(BoxLayout):
    def __init__(self, **kwargs):
        super(Target, self).__init__(**kwargs)


class MyPopup(Popup):
    def __init__(self, **kwargs):
        super(MyPopup, self).__init__(**kwargs)
    def dismiss_popup(self):
        self.dismiss()

class Downloader(BoxLayout):

    def sizeof_fmt(self,num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.2f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.2f%s%s" % (num, 'Yi', suffix)

    def clear_all(self):
        self.ids.download_list.clear_widgets()

    def restart(self):
        #write code
        btnclose = Button(text='Cerrar', size_hint_y=None, height=50)
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='[SUCCESS] Restablecido'))
        content.add_widget(btnclose)
        popup = Popup(content=content, title='Servicio Restablecido',
                      size_hint=(None, None), size=(350, 350),
                      auto_dismiss=False)
        btnclose.bind(on_release=popup.dismiss)
        button = Button(text='Open popup', size_hint=(None, None),
                        size=(150, 70))
        button.bind(on_release=popup.open)
        popup.open()
        #col = AnchorLayout()
        #col.add_widget(button)
        #return col

    def emergente(self):
        popup = MyPopup()
        popup.open()

    def download_file(self,url):
        if "rayserver.dl/" in url:
            thread = threading.Thread(target=self._download_file, args=(url,))
            thread.start()

    def download_file_2(self):
        url = Clipboard.paste()
        logging.info('0 Iniciando '+url)
        #if url and 'https://rayserver.downloader/' in url:
        thread = threading.Thread(target=self._download_file, args=(url,))
        thread.start()

    def _download_file(self, url):
        filename = url.split("/")[-1]
        ruta = url.split(filename)[0]
        pext = "other.png"
        if ".apk" in filename or ".xapk" in filename:
            pext = "apk.png"
        elif ".exe" in filename:
            pext = "exe.png"
        elif ".mp3" in filename or ".m4a" in filename or ".ogg" in filename:
            pext = "music.png"
        elif ".mp4" in filename or ".mkv" in filename or ".avi" in filename or ".mpg" in filename:
            pext = "videos.png"
        elif ".7z" in filename or ".zip" in filename or ".tar" in filename:
            pext = "winrar.png"
        self.add_download(filename, ruta, pext)
        for i in range(0,101):
            self.update_download("file.mp4", i, 100)

    def add_download(self, filename, file_path,pext):
        try:
            target = Target()
            target.filename = filename
            target.file_path = file_path
            target.ids.photo_ext.source = pext
            target.ids.label_text.text = filename
            target.ids.label_text_2.text = "0 MiB de 0 MiB [0%]"
            self.ids.download_list.add_widget(target)
            self.ids.url_input.text = ''
        except Exception as ex:
            logging.info("ex "+str(ex))
            return

    def update_download(self, filename, downloaded, total_length):
        #for download_item in self.ids.download_list.children:
        #    if download_item.filename == filename:
        #        logging.info(str(downloaded))
        #        download_item.ids.label_text_2.text = ">"+str(downloaded)+"de"+str(total_length)+"["+str(downloaded)+" %]"
        try:
            download_item = next((c for c in self.ids.download_list.children if c.filename == filename), None)
            if download_item:
                parte = self.sizeof_fmt(downloaded)
                total = self.sizeof_fmt(total_length)
                porc = str(int(downloaded / total_length * 100))[:4]
                download_item.ids.label_text_2.text = ">"+parte+" de "+total+" ["+porc+" %]"
        except Exception as ex:
            logging.info("ex "+str(ex))
            pass
    #    try:
    #        for download_item in self.ids.download_list.children:
    #            if download_item.filename == filename:
    #                parte = downloaded
    #                total = total_length
    #                porc = str(int(downloaded / total_length * 100))[:4]
    #                download_item.ids.label_text_2.text = f"> {parte} de {total} [{porc} %]"
    #    except Exception as ex:
    #        logging.info("ex "+str(ex))
    #        return

class RayServerdlApp(App):
    
    def build(self):
        return Downloader()

if __name__ in ('__main__', '__android__'):
    RayServerdlApp().run()
