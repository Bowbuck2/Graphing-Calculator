from functools import partial
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.widget import Widget

from kivy.lang import Builder

Builder.load_file('Graph/graph.kv')


class Graph(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.axis_x, self.axis_y = self.ids.axis_x, self.ids.axis_y

        Window.bind(on_resize=self.on_window_resize, on_maximize=self.on_maximize, on_minimize=self.on_minimize)
        self.is_resizing = False

        self.resize_width_up, self.resize_width_down = False, False
        self.prev_width = 640

        self.resize_height_up, self.resize_height_down = False, False
        self.prev_height = 640

        self.graph_moving = False

    def home(self):
        """
        Returns User to 0,0
        """

        self.axis_x.pos = self.parent.children[0].width, 0
        self.axis_y.pos = self.parent.children[0].width, 0
        Clock.schedule_once(self.equation_update, .1)

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
        Clock.schedule_once(self.equation_update, .1)

    def equation_update(self, dt):
        """
        Updates Position of Equations
        """
        for data in self.parent.children[0].ids.InputField.ids.layout.children:
            data.equation_update(data.equation)

    def window_marker_gen(self):
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

    def on_minimize(self, *args):
        """
        Removes any Markers Not in the Current View
        """
        print('Fired')
        self.home()

        # for marker in self.axis_x.children:
        #    if marker.x > self.width or marker < 0:
        #        print(f'Remove Marker {int(marker)}')
        #        marker.is_deleted = True
        #        marker.remove_marker()

        # for marker in self.axis_y.children:
        #    if marker.y > self.height or marker < 0:
        #        print(f'Remove Marker {int(marker)}')
        #        marker.is_deleted = True
        #        marker.remove_marker()

    def on_maximize(self, *args):
        Clock.schedule_once(self.equation_update, .1)

        while len(self.axis_x.children) != 0:
            self.axis_x.reset(), self.axis_y.reset()
        self.axis_x.init_children(.1), self.axis_y.init_children(.1)

        while (len(self.axis_x.children) * 64) < self.width:
            self.axis_x.generate('l-r')

        while (len(self.axis_y.children) * 64) < self.height:
            self.axis_y.generate('l-r')

        self.home()

    def on_window_resize(self, window, width, height):
        self.window_marker_gen()
        Clock.schedule_once(self.equation_update, .1)


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


class Axis(Widget):
    marker_zero = NumericProperty(rebind=True)

    def __init__(self, marker_type, marker_diff, **kwargs):
        super().__init__(**kwargs)

        self.marker_type = marker_type
        self.marker_diff = marker_diff

        Clock.schedule_once(self.axis_register, .1)
        Clock.schedule_once(self.init_children, .1)
        Clock.schedule_interval(self.update, .01)

    def axis_register(self, dt):
        if self.marker_type == "MarkerX":
            self.marker = MarkerX
        elif self.marker_type == "MarkerY":
            self.marker = MarkerY

    def update(self, dt):
        self.children = sorted(self.children, key=int)
        self.resize_window_marker()

    def init_children(self, dt):
        """Creating Basic Instance of Children X-Markers"""
        for key in range(-5, 6, 1):
            marker = self.marker(self.parent, key)

            if self.marker_type == 'MarkerX':
                marker.x = len(self.children) * self.marker_diff
            else:
                marker.y = len(self.children) * self.marker_diff

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
                marker = self.marker(self.parent, new_key)

                if self.marker_type == 'MarkerX':
                    marker.x = self.children[-1].x + self.marker_diff
                else:
                    marker.y = self.children[-1].y + self.marker_diff

                self.add_widget(marker)
        if type_change == 'r-l':
            new_key = self.children[0].key - 1
            if new_key not in marker_key_l:
                marker = self.marker(self.parent, new_key)

                if self.marker_type == 'MarkerX':
                    marker.x = self.children[0].x - self.marker_diff
                else:
                    marker.y = self.children[0].y - self.marker_diff

                self.add_widget(marker)

    def resize_window_marker(self):
        """
        Adds/Removes Markers Depending on window size
        """
        if self.parent.is_resizing:
            self.children = sorted(self.children, key=int)

            if self.marker_type == 'MarkerX':
                if self.parent.resize_width_up:
                    marker_diff = self.width - self.children[-1].x
                    if marker_diff >= 64:
                        self.generate('l-r')
                if self.parent.resize_width_down:
                    if self.children[-1].x > self.width:
                        self.children[-1].is_deleted = True
                        self.children[-1].remove_marker()
            else:
                if self.parent.resize_height_up:
                    marker_diff = self.height - self.children[-1].y
                    if marker_diff >= 64:
                        self.generate('l-r')
                if self.parent.resize_height_down:
                    if self.children[-1].y > self.height:
                        self.children[-1].is_deleted = True
                        self.children[-1].remove_marker()

    def reset(self):
        for marker in self.children:
            marker.is_deleted = True

        for marker in self.children:
            marker.remove_marker()


class AxisX(Axis):
    def __init__(self, marker_type="MarkerX", marker_diff=64, **kwargs):
        super().__init__(marker_type, marker_diff, **kwargs)


class AxisY(Axis):
    def __init__(self, marker_type="MarkerY", marker_diff=64, **kwargs):
        super().__init__(marker_type, marker_diff, **kwargs)


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

    def remove_marker(self):
        self.parent.remove_widget(self)

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

        if self.key == 0:
            self.axis_y.marker_zero = self.marker_pos

    def add_marker(self, marker_pos):
        if not self.parent.parent.is_resizing:
            if marker_pos + 1 < self.ctx.x:
                self.parent.generate('l-r')
                self.parent.remove_widget(self)
                Clock.unschedule(self.update)
            if marker_pos - 1 > self.ctx.width + self.ctx.parent.children[0].width:
                self.parent.generate('r-l')
                self.parent.remove_widget(self)
                Clock.unschedule(self.update)


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

        if self.key == 0:
            self.axis_x.marker_zero = self.marker_pos

    def add_marker(self, marker_pos):
        if not self.parent.parent.is_resizing:
            if marker_pos < self.ctx.y - 64:
                self.parent.generate('l-r')
                self.parent.remove_widget(self)
                Clock.unschedule(self.update)
            elif marker_pos > self.ctx.height:
                self.parent.generate('r-l')
                self.parent.remove_widget(self)
                Clock.unschedule(self.update)
