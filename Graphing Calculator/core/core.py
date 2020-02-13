from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
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

        Window.bind(on_resize=self.on_window_resize)
        self.is_resizing = False

        self.resize_width_up, self.resize_width_down = False, False
        self.prev_width = 640

        self.resize_height_up, self.resize_height_down = False, False
        self.prev_height = 600

    def on_touch_move(self, touch):
        """
        Updates Position of AxisX/AxisY
        """
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

    def on_window_resize(self, window, width, height):
        """
        Checks if Graph is Currently Being Resized
        """
        self.is_resizing = True
        Clock.schedule_once(partial(self.check_graph_size, self.width, self.height))

        if self.width > self.prev_width:
            self.resize_width_up = True
        elif self.width < self.prev_width:
            self.resize_width_down = True

        if self.height > self.prev_height:
            self.resize_height_up = True
        elif self.height < self.prev_height:
            self.resize_height_down = True

        Clock.schedule_once(self.resize_reset, .1)

    def check_graph_size(self, width, height, dt):
        """
        Grabbing A Delayed Width/Height For Comparison
        """
        self.prev_width = width
        self.prev_height = height

    def resize_reset(self, dt):
        """
        Resetting Resize Booleans
        """
        self.is_resizing = False
        self.resize_width_up = False
        self.resize_width_down = False
        self.resize_height_up = False
        self.resize_height_down = False


class AxisX(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_children, .1)
        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.marker_window_update()
        self.resize_window_marker()


    def init_children(self, dt):
        """Creating Basic Instance of Children X-Markers"""
        for key in range(-5, 6, 1):
            marker = MarkerX(self.parent, key)
            marker.x = len(self.children) * 64
            self.add_widget(marker)

    def generate(self, type_change: str):
        """
        Creates New Marker if Left/Right Marker Is Destroyed
        Generates A new Marker On Right/Left
        """
        self.children = sorted(self.children, key=int)
        marker_key_l = [int(marker) for marker in self.children]
        if type_change == 'l-r':
            new_key = self.children[-1].key + 1
            if new_key not in marker_key_l:
                marker = MarkerX(self.parent, new_key)
                marker.x = self.children[-1].x + 64
                self.add_widget(marker)
        if type_change == 'r-l':
            new_key = self.children[0].key - 1
            if new_key not in marker_key_l:
                marker = MarkerX(self.parent, new_key)
                marker.x = self.children[0].x - 64
                self.add_widget(marker)

    def resize_window_marker(self):
        """
        Adds/Removes Markers Depending on window size
        """
        if self.parent.is_resizing:
            self.children = sorted(self.children, key=int)
            if self.parent.resize_width_up:
                marker_diff = self.width - self.children[-1].x
                if marker_diff >= 64:
                    self.generate('l-r')
                    self.generate('r-l')
            if self.parent.resize_width_down:
                if self.children[-1].x > self.width:
                    marker_one, marker_two = self.children[-1], self.children[0]

                    marker_one.is_deleted, marker_two.is_deleted = True, True
                    marker_one.remove_marker(), marker_two.remove_marker()

    def marker_window_update(self):
        """
        Updates Positions Of Markers if Window is Resized
        """
        if self.parent.resize_width_up:
            updated_width = self.width - self.parent.prev_width
            for marker in self.children:
                marker.x += updated_width / 4
        elif self.parent.resize_width_down:
            updated_width = self.parent.prev_width - self.width
            for marker in self.children:
                marker.x -= updated_width / 4


class AxisY(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_children, .1)
        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.marker_window_update()
        self.resize_window_marker()

    def init_children(self, dt):
        """Creating Basic Instance of Children Y-Markers"""
        for key in range(-5, 6, 1):
            marker = MarkerY(self.parent, key)
            marker.y = len(self.children) * 60
            self.add_widget(marker)

    def generate(self, type_change: str):
        """
        Creates New Marker if Left/Right Marker Is Destroyed
        Generates A new Marker On Right/Left
        """
        self.children = sorted(self.children, key=int)
        marker_key_l = [int(marker) for marker in self.children]

        if type_change == 'b-t':
            new_key = self.children[-1].key + 1
            if new_key not in marker_key_l:
                marker = MarkerY(self.parent, new_key)
                marker.y = self.children[-1].y + 60
                self.add_widget(marker)
        if type_change == 't-b':
            new_key = self.children[0].key - 1
            if new_key not in marker_key_l:
                marker = MarkerY(self.parent, new_key)
                marker.y = self.children[0].y - 60
                self.add_widget(marker)

    def resize_window_marker(self):
        """
        Adds/Removes Markers Depending on window size
        """
        if self.parent.is_resizing:
            self.children = sorted(self.children, key=int)
            if self.parent.resize_height_up:
                marker_diff = self.height - self.children[-1].y
                if marker_diff >= 60:
                    self.generate('t-b')
                    self.generate('b-t')
            if self.parent.resize_height_down:
                if self.children[-1].y > self.height:
                    marker_one, marker_two = self.children[-1], self.children[0]

                    marker_one.is_deleted, marker_two.is_deleted = True, True
                    marker_one.remove_marker(), marker_two.remove_marker()

    def marker_window_update(self):
        """
        Updates Positions Of Markers if Window is Resized
        """
        if self.parent.resize_height_up:
            updated_height = self.height - self.parent.prev_height
            for marker in self.children:
                marker.y += updated_height / 3.95
        elif self.parent.resize_height_down:
            updated_height = self.parent.prev_height - self.height
            for marker in self.children:
                marker.y -= updated_height / 3.95


class Marker(Widget):
    """
    Base For MarkerX/MarkerY
    """
    axis_y = ObjectProperty(rebind=True)
    axis_x = ObjectProperty(rebind=True)
    key = NumericProperty()

    def __init__(self, ctx: Graph, key, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.axis_y, self.axis_x = self.ctx.axis_y, self.ctx.axis_x
        self.key = key
        self.is_deleted = False

    def __int__(self):
        return self.key


class MarkerX(Marker):

    def __init__(self, ctx: Graph, key, **kwargs):
        super().__init__(ctx, key, **kwargs)
        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.graph_height = self.ctx.height
        self.axis_x_pos = self.axis_x.y + (self.axis_x.height / 2 - 40)
        self.marker_pos = self.pos[0] + self.axis_y.x

        if not self.is_deleted:
            self.add_marker(self.marker_pos)

    def add_marker(self, marker_pos):
        if marker_pos + 1 < self.ctx.x:
            self.parent.generate('l-r')
            self.parent.remove_widget(self)
            Clock.unschedule(self.update)
        if marker_pos - 1 > self.ctx.width + self.ctx.parent.children[0].width:
            self.parent.generate('r-l')
            self.parent.remove_widget(self)
            Clock.unschedule(self.update)

    def remove_marker(self):
        self.parent.remove_widget(self)


class MarkerY(Marker):

    def __init__(self, ctx: Graph, key, **kwargs):
        super().__init__(ctx, key, **kwargs)
        Clock.schedule_interval(self.update, .01)

    def update(self, dt):
        self.graph_width = self.ctx.width + self.ctx.parent.children[0].width
        self.axis_y_pos = self.axis_y.x + (self.axis_y.width / 2 - 40)
        self.marker_pos = self.pos[1] + self.axis_x.y

        if not self.is_deleted:
            self.add_marker(self.marker_pos)

    def add_marker(self, marker_pos):
        if marker_pos < self.ctx.y:
            self.parent.generate('b-t')
            self.parent.remove_widget(self)
            Clock.unschedule(self.update)
        elif marker_pos > self.ctx.height:
            self.parent.generate('t-b')
            self.parent.remove_widget(self)
            Clock.unschedule(self.update)

    def remove_marker(self):
        self.parent.remove_widget(self)


class SideBar(FloatLayout):
    pass


class InputField(RecycleView):
    pass


class MyApp(App):
    def build(self):
        return Main()
