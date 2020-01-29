from kivy.app import App
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
    pass


class AxisX(FloatLayout):
    pos_hint = DictProperty({'x': 0, 'y': 0.5})
    markers = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mark_gen()

    def mark_gen(self):
        markers_count = 4
        mark_distance = 1 / markers_count

        for mark in range(markers_count):
            marker = Marker()
            marker.text = str(round(mark * mark_distance, 2))
            marker.size_hint = [.05, .4]
            marker.pos_hint = {'x': mark_distance * mark, 'y': 0}
            self.markers.append(marker)
            self.add_widget(marker)

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            speed = 0.0015
            if touch.dy > 0:
                self.pos_hint['y'] += abs(speed * touch.dy)
            elif touch.dy < 0:
                self.pos_hint['y'] -= abs(speed * touch.dy)


class AxisY(FloatLayout):
    pos_hint = DictProperty({'x': 0.5, 'y': 0})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 0.0015

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos):
            if touch.dx > 0:
                self.marker_update(1, touch)
                self.pos_hint['x'] += abs(self.speed * touch.dx)
            elif touch.dx < 0:
                self.marker_update(2, touch)
                self.pos_hint['x'] -= abs(self.speed * touch.dx)

    def marker_update(self, state: int, touch):
        markers = self.parent.ids.X.markers
        for marker in markers:
            if state == 1:
                marker.pos_hint['x'] += abs(self.speed * touch.dx)
            elif state == 2:
                marker.pos_hint['x'] -= abs(self.speed * touch.dx)


class Marker(Label):
    pass


class SideBar(FloatLayout):
    pass


class InputField(RecycleView):
    pass


class MyApp(App):
    def build(self):
        return Main()
