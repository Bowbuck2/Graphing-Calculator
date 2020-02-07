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

        self.values = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        self.increase_x, self.increase_y = 10, 10
        self.decrease_x, self.decrease_y = 0, 0

        Clock.schedule_once(self.mark_init, .1)

    def mark_init(self, dt):
        self.mark_gen('x')
        self.mark_gen('y')

    def mark_gen(self, type: str):
        if type == 'x':
            for length, key in enumerate(self.values):
                marker = MarkerX(self, key)
                marker.x = length * 64
                self.x_marker.append(marker)
                self.axis_x.add_widget(marker)
        if type == 'y':
            for length, key in enumerate(self.values):
                marker = MarkerY(self, key)
                marker.y = length * 60
                self.y_marker.append(marker)
                self.axis_y.add_widget(marker)

    def generate(self, type_change: str, marker_type):
        if type_change == '->':
            print(f'Deleted Marker {self.values[0]}')
            new_key = self.values[-1] + 1

            self.values.append(new_key)

            if marker_type == AxisX:
                self.increase_x += 1
                self.decrease_x += 1
                marker = MarkerX(self, new_key)
                marker.x = self.increase_x * 64
            else:
                self.increase_y += 1
                self.decrease_y += 1
                marker = MarkerY(self, new_key)
                marker.y = self.increase_y * 60
            self.axis_y.add_widget(marker)
            self.values.pop(0)

            print(f'Generated Marker {new_key}')
        elif type_change == '<-':
            print(f'Deleted Marker {self.values[-1]}')
            new_key = self.values[0] - 1

            self.values.insert(0, new_key)

            if marker_type == AxisX:
                self.decrease_x -= 1
                self.increase_x -= 1
                marker = MarkerX(self, new_key)
                marker.x = self.decrease_x * 64
            else:
                self.decrease_y -= 1
                self.increase_y -= 1
                marker = MarkerY(self, new_key)
                marker.y = self.decrease_y * 60

            self.axis_x.add_widget(marker)
            self.values.pop(-1)

            print(f'Generated Marker {new_key}')

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

        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.graph_height = self.ctx.height

        parent_width = self.ctx.width
        self.marker_window_update(parent_width)

        marker_pos = self.pos[0] + self.axis_y.x
        self.add_marker(marker_pos)

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

        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.graph_width = self.ctx.width + 160

        parent_height = self.ctx.height
        self.marker_window_update(parent_height)

        marker_pos = self.pos[1] + self.axis_x.y
        self.add_marker(marker_pos)

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
