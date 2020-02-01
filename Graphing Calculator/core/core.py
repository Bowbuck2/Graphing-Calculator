from kivy.app import App
from kivy.properties import DictProperty, ListProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView


class Main(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Graph(pos_hint={'right': 1}, size_hint=[.8, 1]))
        self.add_widget(SideBar(pos_hint={'left': 0}, size_hint=[.2, 1]))


class Graph(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.axis_y = AxisY(size_hint=[1, 1], ctx=self)
        self.axis_x = AxisX(size_hint=[1, 1], ctx=self)
        self.add_widget(self.axis_x)
        self.add_widget(self.axis_y)

        self.markers_count = 4
        self.mark_distance = 1 / self.markers_count
        self.markers_x = []
        self.markers_y = []
        self.mark_init()

    def mark_init(self):
        self.mark_gen('x')
        self.mark_gen('y')

    def mark_gen(self, axis):
        for mark in range(self.markers_count):
            marker = Marker()
            if axis == 'x':
                marker.size_hint = [.01, .02]
                marker.pos_hint = {'x': self.mark_distance * mark + .1, 'y': self.axis_x.pos_hint['x'] - .007}
                self.markers_x.append(marker)
                self.axis_x.add_widget(marker)
            elif axis == 'y':
                marker.size_hint = [.02, .01]
                marker.pos_hint = {'x': self.axis_y.pos_hint['y'] - .007, 'y': self.mark_distance * mark + .1}
                self.markers_y.append(marker)
                self.axis_y.add_widget(marker)


class AxisX(FloatLayout):
    pos_hint = DictProperty({'x': 0, 'y': 0.5})
    markers = ListProperty()
    y_axis = ObjectProperty()

    def __init__(self, ctx: Graph, **kwargs):
        super().__init__(**kwargs)
        self.y_axis = ctx.axis_y
        print(self.y_axis.y)

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
    x_axis = ObjectProperty()

    def __init__(self, ctx: Graph, **kwargs):
        super().__init__(**kwargs)
        print(ctx.axis_x)

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
