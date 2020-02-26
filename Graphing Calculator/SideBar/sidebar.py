from random import randrange

import re

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.uix.textinput import TextInput

Builder.load_file('Sidebar/sidebar.kv')


class SideBar(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_start, .1)

    def init_start(self, dt):
        self.graph = self.parent.children[1]


class InputField(RecycleView):
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

        self.points = []

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
            self.clear_canvas()
            self.function_create()

    def function_create(self):
        """
        Creates the function on the graph
        """
        axis_x = self.ctx.parent.graph.axis_x
        axis_y = self.ctx.parent.graph.axis_y

        equation_right = self.equation.split('=')[1].lower()
        variables = []

        for count, char in enumerate(equation_right):
            if char.isalpha():
                variables.append(tuple([char, count]))

        symbol = variables[0]
        cord_points = []

        try:
            for x_value in axis_x.children:
                equation = list(equation_right)
                equation[symbol[1]] = str(x_value.key)
                y_key = eval(''.join(char for char in equation))
                for y_value in axis_y.children:
                    if y_value.key == y_key:
                        cord_points.append(tuple([int(x_value.marker_pos), int(y_value.marker_pos)]))
        except (SyntaxError, TypeError):
            pass

        with self.ctx.parent.graph.canvas:
            self.line = Line(points=cord_points, width=1.5, color=Color(self.r, self.g, self.b, 1), dash=False)

    def remove_equation(self):
        """
        Removes Self
        """
        self.ctx.data.pop(self.position)
        self.ctx.update_position()
        self.clear_canvas()

    def clear_canvas(self):
        """
        Checks if canvas line exists, then deletes
        """
        try:
            self.ctx.parent.graph.canvas.remove(self.line)
        except AttributeError:
            pass

    def __dict__(self):
        return self.dat


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
