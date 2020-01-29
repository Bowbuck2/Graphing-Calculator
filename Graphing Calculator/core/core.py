from kivy.app import App
from kivy.properties import NumericProperty, DictProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.widget import Widget


class Main(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Graph(pos_hint={'right': 1}, size_hint=[.8, 1]))
        self.add_widget(SideBar(pos_hint={'left': 0}, size_hint=[.2, 1]))


class Graph(FloatLayout):
    pass


class AxisX(Widget):
    pos_hint = DictProperty({'x': 0, 'y': 0.5})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            if touch.dy > 0:
                self.pos_hint['y'] += abs(.005 * touch.dy)
            elif touch.dy < 0:
                self.pos_hint['y'] -= abs(.005 * touch.dy)


class AxisY(Widget):
    pos_hint = DictProperty({'x': 0.5, 'y': 0})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            if touch.dx > 0:
                self.pos_hint['x'] += abs(.005 * touch.dx)
            elif touch.dx < 0:
                self.pos_hint['x'] -= abs(.005 * touch.dx)


class SideBar(FloatLayout):
    pass


class InputField(RecycleView):
    pass



class MyApp(App):
    def build(self):
        return Main()
