from kivy.app import App
from kivy.clock import Clock
from kivy.properties import DictProperty, ObjectProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView


class Main(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Graph(pos_hint={'right': 1}, size_hint=[.8, 1]))
        self.add_widget(SideBar(pos_hint={'left': 0}, size_hint=[.2, 1]))


class Graph(FloatLayout):
    pass


class AxisX(FloatLayout):
    pos_hint = DictProperty({'x': 0, 'y': 0.5})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markers_count = 5
        self.mark_distance = 1 / self.markers_count

        Clock.schedule_once(self.mark_gen, 1)

    def mark_gen(self, dt):
        mark_values = {-2: -300, -1: -150, 1: 130, 2: 300}
        for key, value in mark_values.items():
            marker = MarkerX(self)
            marker.text = str(key)
            marker.size_hint = [.01, .02]
            marker.x = value
            marker.pos_hint['y'] = self.pos_hint['x']
            self.add_widget(marker)

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            speed = 0.0015
            if touch.dy > 0:
                self.pos_hint['y'] += abs(speed * touch.dy)
            elif touch.dy < 0:
                self.pos_hint['y'] -= abs(speed * touch.dy)


class MarkerX(Label):
    axis_y = ObjectProperty(rebind=True)

    def __init__(self, ctx: AxisX, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.axis_y = self.ctx.parent.ids.axis_y



class AxisY(FloatLayout):
    pos_hint = DictProperty({'x': 0.5, 'y': 0})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.markers_count = 4
        self.mark_distance = 1 / self.markers_count

        Clock.schedule_once(self.mark_gen, 1)

    def mark_gen(self, dt):
        for mark in range(self.markers_count):
            marker = MarkerY(self)
            marker.size_hint = [.02, .01]
            marker.pos_hint = {'x': self.pos_hint['y'] - .007, 'y': self.mark_distance * mark - .4}
            self.add_widget(marker)

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            speed = 0.0015
            if touch.dx > 0:
                self.pos_hint['x'] += abs(speed * touch.dx)
            elif touch.dx < 0:
                self.pos_hint['x'] -= abs(speed * touch.dx)


class MarkerY(Label):
    axis_x = ObjectProperty(rebind=True)

    def __init__(self, ctx: AxisY, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.axis_x = self.ctx.parent.ids.axis_x


class SideBar(FloatLayout):
    pass


class InputField(RecycleView):
    pass


class MyApp(App):
    def build(self):
        return Main()
