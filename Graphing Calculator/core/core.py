from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import DictProperty, ObjectProperty, NumericProperty
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
        self.axis_x, self.axis_y = self.ids.axis_x, self.ids.axis_y
        self.x_marker, self.y_marker = [], []

        self.values_x = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        self.values_y = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        self.increase_x, self.increase_y = 10, 10
        self.decrease_x, self.decrease_y = 0, 0

        Clock.schedule_once(self.mark_init, .1)

    def mark_init(self, dt):
        self.mark_gen('x')
        self.mark_gen('y')

    def mark_gen(self, type: str):
        if type == 'x':
            for length, key in enumerate(self.values_x):
                marker = MarkerX(self, key)
                marker.x = length * 64
                self.x_marker.append(marker)
                self.axis_x.add_widget(marker)
        if type == 'y':
            for length, key in enumerate(self.values_y):
                marker = MarkerY(self, key)
                marker.y = length * 60
                self.y_marker.append(marker)
                self.axis_y.add_widget(marker)

    def generate(self, type_change: str, marker_type):
        if type_change == '->':
            if marker_type == AxisX:
                new_key = self.values_x[-1] + 1
                self.values_x.append(new_key)
                self.increase_x += 1
                self.decrease_x += 1
                marker = MarkerX(self, new_key)
                marker.x = self.increase_x * 64
                self.axis_x.add_widget(marker)
                self.values_x.pop(0)
            else:
                new_key = self.values_y[-1] + 1
                self.values_y.append(new_key)
                self.increase_y += 1
                self.decrease_y += 1
                marker = MarkerY(self, new_key)
                marker.y = self.increase_y * 60
                self.axis_y.add_widget(marker)
                self.values_y.pop(0)

        elif type_change == '<-':
            if marker_type == AxisX:
                new_key = self.values_x[0] - 1
                self.values_x.insert(0, new_key)
                self.decrease_x -= 1
                self.increase_x -= 1
                marker = MarkerX(self, new_key)
                marker.x = self.decrease_x * 64
                self.axis_x.add_widget(marker)
                self.values_x.pop(-1)
            else:
                new_key = self.values_y[0] - 1
                self.values_y.insert(0, new_key)
                self.decrease_y -= 1
                self.increase_y -= 1
                marker = MarkerY(self, new_key)
                marker.y = self.decrease_y * 60
                self.axis_y.add_widget(marker)
                self.values_y.pop(-1)

    def on_touch_move(self, touch):
        speed = 1
        if self.collide_point(*touch.pos):
            if touch.dy > 0:
                self.axis_x.y += abs(speed * touch.dy)
            elif touch.dy < 0:
                self.axis_x.y -= abs(speed * touch.dy)
            if touch.dx > 0:
                self.axis_y.x += abs(speed * touch.dx)
            elif touch.dx < 0:
                self.axis_y.x -= abs(speed * touch.dx)


class MarkerX(Widget):
    axis_y = ObjectProperty(rebind=True)
    axis_x = ObjectProperty(rebind=True)
    key = NumericProperty()

    def __init__(self, ctx: Graph, key, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.axis_y, self.axis_x = self.ctx.axis_y, self.ctx.axis_x
        self.prev_window_size = 640
        self.key = key
        self.marker_pos = self.pos[0] + self.axis_y.x

        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.graph_height = self.ctx.height
        self.axis_x_pos = self.axis_x.y + (self.axis_x.height / 2 - 40)

        parent_width = self.ctx.width
        self.marker_window_update(parent_width)

        self.marker_pos = self.pos[0] + self.axis_y.x
        self.add_marker(self.marker_pos)

    def add_marker(self, marker_pos):
        if marker_pos < self.ctx.x:
            self.ctx.generate('->', AxisX)

            self.ctx.axis_x.remove_widget(self)
            Clock.unschedule(self.update, '->')
        elif marker_pos > self.ctx.width + 224:
            self.ctx.generate('<-', AxisX)

            self.ctx.axis_x.remove_widget(self)
            Clock.unschedule(self.update, '<-')

    def marker_window_update(self, parent_width):
        if parent_width > self.prev_window_size:
            new_width = parent_width - self.prev_window_size
            self.x += new_width / 2
            self.prev_window_size = parent_width
        elif parent_width < self.prev_window_size:
            new_width = self.prev_window_size - parent_width
            self.x -= new_width / 2
            self.prev_window_size = parent_width


class MarkerY(Label):
    axis_y = ObjectProperty(rebind=True)
    axis_x = ObjectProperty(rebind=True)
    key = NumericProperty()

    def __init__(self, ctx: Graph, key, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.axis_y, self.axis_x = self.ctx.axis_y, self.ctx.axis_x
        self.prev_window_size = 600
        self.key = key
        self.marker_pos = self.pos[1] + self.axis_x.y

        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.graph_width = self.ctx.width + 160
        self.axis_y_pos = self.axis_y.x + (self.axis_y.width / 2 - 40)

        parent_height = self.ctx.height
        self.marker_window_update(parent_height)

        self.marker_pos = self.pos[1] + self.axis_x.y
        self.add_marker(self.marker_pos)

    def add_marker(self, marker_pos):
        if marker_pos < self.ctx.y - 64:
            self.ctx.generate('->', AxisY)

            self.ctx.axis_y.remove_widget(self)
            Clock.unschedule(self.update, '->')
        elif marker_pos > self.ctx.height:
            self.ctx.generate('<-', AxisY)

            self.ctx.axis_y.remove_widget(self)
            Clock.unschedule(self.update, '<-')

    def marker_window_update(self, parent_height):
        if parent_height > self.prev_window_size:
            new_width = parent_height - self.prev_window_size
            self.y += new_width / 2
            self.prev_window_size = parent_height
        elif parent_height < self.prev_window_size:
            new_width = self.prev_window_size - parent_height
            self.y -= new_width / 2
            self.prev_window_size = parent_height


class AxisX(Widget):
    pass


class AxisY(Widget):
    pass


class SideBar(FloatLayout):
    pass


class InputField(RecycleView):
    pass


class MyApp(App):
    def build(self):
        return Main()
