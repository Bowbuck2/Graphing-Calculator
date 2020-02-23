from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder

Builder.load_file('Sidebar/sidebar.kv')


class SideBar(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_start, .1)

    def init_start(self, dt):
        self.graph = self.parent.children[1]


class InputField(RecycleView):
    pass
