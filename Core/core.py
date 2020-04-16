from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

from Graph.graph import Graph
from SideBar.sidebar import SideBar


class Main(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Graph(pos_hint={'right': 1}, size_hint=[.8, 1]))
        self.add_widget(SideBar(pos_hint={'left': 0}, size_hint=[.2, 1]))


class CoreApp(App):
    def build(self):
        self.title = 'Graphing Calculator'
        return Main()
