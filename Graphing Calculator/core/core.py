from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, DictProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.widget import Widget


class Main(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Graph(pos_hint={'right': 1}, size_hint=[.8, 1]))
        self.add_widget(SideBar(pos_hint={'left': 0}, size_hint=[.2, 1]))


class Graph(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.markers_count = 4
        self.mark_distance = 1 / self.markers_count
        self.markers_x = []
        self.markers_y = []
        self.mark_init()

        Clock.schedule_interval(self.marker_update, 0.00001)

    def mark_init(self):
        self.mark_gen('x')

    def mark_gen(self, axis):
        for mark in range(self.markers_count):
            marker = Marker()
            marker.text = str(round(mark * self.mark_distance, 2))
            if axis == 'x':
                marker.size_hint = [.06, .02]
                marker.pos_hint = {'x': self.ids.Y.pos_hint['x'], 'y': self.mark_distance * mark}
                self.markers_x.append(marker)
                self.ids.X.add_widget(marker)
            elif axis == 'y':
                marker.size_hint = [.06, .02]
                marker.pos_hint = {'x': self.mark_distance * mark, 'y': .5}
                self.markers_y.append(marker)
                self.ids.Y.add_widget(marker)

    def marker_update(self, dt):

        for marker in self.markers_y:
            marker.pos_hint['y'] = self.ids.X.pos_hint['y']
        for marker in self.markers_x:
            marker.pos_hint['x'] = self.ids.Y.pos_hint['x']


class AxisX(FloatLayout):
    pos_hint = DictProperty({'x': 0, 'y': 0.5})
    markers = ListProperty()

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            speed = 0.0015
            if touch.dy > 0:
                self.pos_hint['y'] += abs(speed * touch.dy)
            elif touch.dy < 0:
                self.pos_hint['y'] -= abs(speed * touch.dy)


class AxisY(FloatLayout):
    pos_hint = DictProperty({'x': 0.5, 'y': 0})
    markers = ListProperty()

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            speed = 0.0015
            if touch.dx > 0:
                self.pos_hint['x'] += abs(speed * touch.dx)
            elif touch.dx < 0:
                self.pos_hint['x'] -= abs(speed * touch.dx)


class Marker(Label):
    pass


class SideBar(FloatLayout):
    pass


class InputField(RecycleView):
    pass


class MyApp(App):
    def build(self):
        return Main()
