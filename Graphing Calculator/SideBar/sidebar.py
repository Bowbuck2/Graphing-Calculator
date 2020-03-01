import math
from random import randrange
import re

from kivy.clock import Clock
from kivy.graphics.context_instructions import Color, Translate, PushMatrix, PopMatrix
from kivy.graphics.vertex_instructions import Line
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, ColorProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

Builder.load_file('Sidebar/sidebar.kv')


class SideBar(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_start, .1)

    def init_start(self, dt):
        self.graph = self.parent.children[1]


class RV(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

        Clock.schedule_once(self.init_gen, .1)
        Clock.schedule_interval(self.update, .1)

    def update(self, dt):
        self.equation_gen_check()

    def equation_gen_check(self):
        """
        Generates another Equation if All are filled
        """
        if not any(data.get('equation', None) == '' for data in self.data):
            self.data.append(Equation(position=self.data[-1].get('position') + 1, ctx=self).__dict__())

    def update_position(self):
        """
        Updates Positions after Labels are Removed
        """
        for count, data in enumerate(self.data):
            data['position'] = count

    def init_gen(self, dt):
        """
        on app start, will generate EquationInput
        """
        for amount in range(0, 1):
            equation_input = Equation(position=amount, ctx=self)
            self.data.append(equation_input.__dict__())


class Equation(FloatLayout):
    r, g, b = NumericProperty(), NumericProperty(), NumericProperty()
    equation = StringProperty()
    position = NumericProperty(0)
    ctx = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ctx, self.position = kwargs.get('ctx'), kwargs.get('position') or 0
        self.equation = ''

        self.r, self.g, self.b = round(randrange(1, 255) / 255, 2), round(randrange(1, 255) / 255, 2), round(
            randrange(1, 255) / 255, 2)

        self.dat = {'position': int(self.position), 'r': float(self.r), 'g': float(self.g), 'b': float(self.b),
                    'equation': str(self.equation), 'ctx': self.ctx}

        self.variables = []
        self.equation_right = ''
        self.symbol = 0

        self.x_values, self.y_values = [], []
        self.x_cord, self.y_cord = [], []
        self.cord_points = []

        Clock.schedule_once(self.grab_parents, .1)

    def grab_parents(self, dt):
        self.axis_x = self.ctx.parent.graph.axis_x
        self.axis_y = self.ctx.parent.graph.axis_y

    def equation_update(self, equation_text):
        """
        updates RV data of equation input
        checks if equation is a function
        """
        for data in self.ctx.data:
            if data['position'] == self.position:
                data['equation'] = equation_text
                self.equation = equation_text

        if re.match(r'.?=.+', equation_text):
            self.function_create()

    def function_create(self):
        """
        Creates Key Values
        """
        self.cord_points = []
        self.x_cord, self.y_cord = [], []
        self.x_values, self.y_values = [], []

        self.equation_right = self.equation.split('=')[1].lower()

        for count, char in enumerate(self.equation_right):
            if char.isalpha():
                self.variables.append(tuple([char, count]))

        self.symbol = self.variables[0]

        x_child = self.axis_x.children
        x_key = x_child[0].key - .125

        # PARENT KEY DOES NOT EXIST
        for pixel in range(int(x_child[0].marker_pos), int(x_child[-1].marker_pos), 8):
            # Sets X Value
            x_key += .125
            self.x_cord.append(pixel)
            self.x_values.append(round(x_key, 2))

            # Sets Y Values (Plug X into Y)
            equation = list(self.equation_right)
            equation[self.symbol[1]] = str(round(x_key, 2))
            y_key = eval(''.join(char for char in equation))
            self.y_values.append(y_key)

        for y_value in self.y_values:
            parent_key = math.ceil(y_value)

            if parent_key != y_value:
                key_diff = abs(round(abs(parent_key) - abs(y_value), 2))

                offset = {
                    .12: 8,
                    .25: 16,
                    .38: 24,
                    .5: 32,
                    .62: 40,
                    .75: 48,
                    .88: 56
                }.get(key_diff)

                if parent_key in [marker.key for marker in self.axis_y.children]:
                    for marker in self.axis_y.children:
                        if marker.key == parent_key:
                            self.y_cord.append(marker.marker_pos - offset)
                else:
                    self.y_cord.append((self.axis_y.children[-1].marker_pos + 64) - offset)
            else:
                for marker in self.axis_y.children:
                    if marker.key == int(parent_key):
                        self.y_cord.append(marker.marker_pos)

        self.cord_points = [tuple([x_cord, y_cord]) for x_cord, y_cord in zip(self.x_cord, self.y_cord)]

        self.add_widget(LineDraw(ctx=self))

    def __dict__(self):
        return self.dat


class LineDraw(Widget):
    ctx = ObjectProperty(None)

    cord_points = ListProperty()
    line_color = ColorProperty()

    line_anchor_x = NumericProperty()
    line_anchor_y = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx = kwargs.get('ctx')
        self.graph = self.ctx.parent.parent.parent.graph

        self.cord_points = self.ctx.cord_points
        self.line_color = self.ctx.r, self.ctx.g, self.ctx.b, 1

        self.line_anchor_x = self.graph.axis_x.children[5].marker_pos
        self.line_anchor_y = self.graph.axis_y.children[5].marker_pos


class EquationInput(TextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Removes if Equation is empty and keycode is fired
        """
        super().keyboard_on_key_down(window, keycode, text, modifiers)
        if self.text == "" and len(self.parent.ctx.data) > 2:
            if keycode[1] == "backspace":
                print(self.parent.remove_equation())
        return True

    def insert_text(self, substring, from_undo=False):
        s = substring.lower()
        if not s.isspace():
            return super(EquationInput, self).insert_text(s, from_undo=from_undo)
