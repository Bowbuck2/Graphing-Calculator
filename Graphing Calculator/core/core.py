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

        Clock.schedule_once(self.mark_init, .1)

    def mark_init(self, dt):
        self.mark_gen('x')

    def mark_gen(self, type: str):
        if type == 'x':
            for length, key in enumerate(self.values):
                marker = MarkerX(self, key)
                marker.x = length * 64
                self.x_marker.append(marker)
                self.axis_x.add_widget(marker)

    def generate(self, type: str):
        if type == '->':
            new_key = self.values[-1] + 1

            self.values.append(new_key)

            marker = MarkerX(self, new_key)
            marker.x = self.values[-1] * 64
            self.axis_x.add_widget(marker)
            self.values.pop(0)

            print(f'Generated Marker {new_key}')
        elif type == '<-':
            new_key = self.values[0] - 1

            self.values.append(new_key)

            marker = MarkerX(self, new_key)
            marker.x = self.values[0] * 64
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
        self.axis_y = self.ctx.axis_y
        self.axis_x = self.ctx.axis_x
        self.key = key

        Clock.schedule_interval(self.update, .1)

    def update(self, dt):
        self.graph_height = self.ctx.height

        marker_pos = self.pos[0] + self.axis_y.x

        # self.ctx.parent.x#
        if marker_pos < 160:
            print(f'Deleted Marker {self.key}')
            self.ctx.generate('->')

            self.ctx.axis_x.remove_widget(self)
            Clock.unschedule(self.update, '->')
        # elif marker_pos > 800:
        #    print(f'Deleted Marker {self.key}')
        #    self.ctx.generate('<-')

        #    self.ctx.axis_x.remove_widget(self)
        #    Clock.unschedule(self.update, '->')


class MarkerY(Label):
    axis_x = ObjectProperty(rebind=True)
    graph_width = NumericProperty()

    def __init__(self, ctx: Graph, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.axis_x = self.ctx.axis_x

        Clock.schedule_interval(self.update, .1)

    def update(self, dt):
        self.graph_width = self.ctx.width + 160


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
