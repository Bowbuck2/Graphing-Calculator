import math
import re
from random import randrange

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.textinput import TextInput

Builder.load_file('SideBar/sidebar.kv')


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


class Solver:
    def __init__(self, equation: str) -> None:
        self.operations = {'^': float.__pow__, '*': float.__mul__, '/': float.__truediv__, '+': float.__add__,
                           '-': float.__sub__, }
        self.equation = equation.split('=')[1]

    def start(self, **kwargs):
        eq = list(''.join(self.equation))

        for count, char in enumerate(eq):
            if char in kwargs.keys():
                value = kwargs[char]
                eq[count] = str(value)

        if '(' in eq:
            right_p, left_p = None, None

            for count, char in enumerate(eq):
                if char == '(':
                    left_p = count
                elif char == ')':
                    right_p = count + 1

                if right_p and left_p is not None and len(self.equation) != 1:
                    ans = str(self.solve(eq[left_p:right_p]))

                    eq = eq[:left_p] + eq[right_p:]
                    eq.insert(left_p, ans)

                    self.equation = eq
                    self.start(**kwargs)
                elif len(self.equation) == 1:
                    return float(self.equation[0])
        else:
            return self.solve(eq)

    def solve(self, equation: list):
        ans = None
        values = []
        temp = ''
        for count, char in enumerate(equation):
            if char == '-':
                values.append('-1.0')
                values.append('*')
                continue

            if char not in self.operations.keys() and char not in ['(', ')']:
                temp += char
            else:
                values.append(temp)
                values.append(char)
                temp = ''
        if len(temp) != 0:
            values.append(temp)

        if len(values) == 1:
            return float(values[0])

        for key, value in self.operations.items():
            if key in values:
                index = values.index(key)

                left_value = float(values[index - 1])
                right_value = float(values[index + 1])

                if right_value < 0.9 and '^' in values:
                    left_value = abs(left_value)

                ans = value(left_value, right_value)

                values.pop(index + 1)
                values[index - 1] = ans
                values.pop(index)

        return ans


class Equation(FloatLayout):
    r, g, b = NumericProperty(), NumericProperty(), NumericProperty()
    equation = StringProperty()
    position = NumericProperty(0)
    ctx = ObjectProperty(None)
    translate_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx, self.position = kwargs.get('ctx'), kwargs.get('position') or 0
        self.equation = ''

        self.line = []
        self.data = ListProperty(None)
        self.points = []

        self.r, self.g, self.b = round(randrange(1, 255) / 255, 2), round(randrange(1, 255) / 255, 2), round(
            randrange(1, 255) / 255, 2)

        self.dat = {'position': int(self.position), 'r': float(self.r), 'g': float(self.g), 'b': float(self.b),
                    'equation': str(self.equation), 'ctx': self.ctx}

        Clock.schedule_once(self.grab_parents, .1)

    def grab_parents(self, dt):
        self.graph = self.ctx.parent.graph
        self.axis_x = self.graph.axis_x
        self.axis_y = self.graph.axis_y

    def equation_check(self, equation_text: str):
        """
        updates RV data of equation input
        checks if equation is a function
        """
        for data in self.ctx.data:
            if data['position'] == self.position:
                data['equation'] = equation_text
                self.equation = equation_text  # [-]?(\d | \w)
        if re.match(r'(y|x|(f\(x\)))=.+', self.equation.lower()):
            self.remove_line()

            if self.equation[0] is not 'x':
                self.create_equation()
            else:
                self.vert_equation()

            self.gen_line()
        else:
            self.remove_line()

    def create_equation(self):
        """
        Creates X/Y Values
        """
        parent_data_x = []

        for marker in self.graph.axis_x.children:
            try:
                parent_data_x.append({'parent_pos': round(marker.marker_pos, 2), 'key_value': marker.key})
            except TypeError:
                pass

        parent_data_x.append(
            {'parent_pos': parent_data_x[-1]['parent_pos'] + 60, 'key_value': parent_data_x[-1]['key_value'] + 1})

        count = 0
        for x_pos in range(0, Window.width, 5):
            x_pos_updated = x_pos + self.graph.x
            try:
                if x_pos_updated <= parent_data_x[count].get('parent_pos'):
                    parent_key_value_x = parent_data_x[count].get('key_value')
                    x_value = round(
                        parent_key_value_x - (((parent_data_x[count].get('parent_pos')) - (x_pos + self.graph.x)) / 60),
                        2)

                    parent_pos_y, y_pos, y_value, parent_key_value_y = self.equate_y(x_value)

                    self.data.append({'x_value': x_value, 'x_pos': x_pos_updated, 'y_value': y_value, 'y_pos': y_pos,
                                      'parent_pos_x': int(parent_data_x[count].get('parent_pos')),
                                      'parent_key_value_x': parent_key_value_x, 'parent_pos_y': parent_pos_y,
                                      'parent_key_value_y': parent_key_value_y})
                else:
                    count += 1
            except (IndexError, TypeError):
                pass

    def equate_y(self, x_value: float):
        """
        Solves for Y Value
        """
        parent_pos_y = None

        solver = Solver(self.equation)
        y_value = solver.start(x=x_value)
        parent_key_value_y = math.ceil(y_value)

        for marker in self.axis_y.children:
            if marker.key == parent_key_value_y:
                parent_pos_y = marker.marker_pos

        if parent_pos_y is None:
            key = self.axis_y.children[-1].key
            if y_value > key and parent_key_value_y <= key + 1:
                parent_pos_y = self.axis_y.children[-1].marker_pos + 60

        y_pos = (parent_pos_y - (abs(parent_key_value_y - y_value) * 60))

        print(f'At {x_value}, Our y-value is {y_value}')
        return parent_pos_y, y_pos, y_value, parent_key_value_y

    def vert_equation(self):
        try:
            parent_pos = None

            solver = Solver(self.equation)
            x_value = solver.start()
            parent_value = math.ceil(x_value)

            for marker in self.axis_x.children:
                if marker.key == parent_value:
                    parent_pos = marker.marker_pos

            dif = parent_value - x_value
            value_pos = dif * 60
            value = parent_pos - value_pos

            self.data.append(
                {'x_pos': value, 'y_pos': self.graph.y, 'parent_pos_x': parent_pos, 'parent_pos_y': parent_pos})
            self.data.append(
                {'x_pos': value, 'y_pos': self.graph.height, 'parent_pos_x': parent_pos, 'parent_pos_y': parent_pos})

        except TypeError:
            pass

    def gen_line(self):
        """
        Updates Current Lines or Generates new ones
        """
        self.points = [tuple([dat.get('x_pos'), dat.get('y_pos')]) for dat in self.data]

        for l in self.line:
            self.graph.canvas.remove(l)
        with self.graph.canvas:
            line = Line(points=self.points, width=1.5, color=Color(self.r, self.g, self.b, 1))

        self.line = []
        self.line.append(line)

    def remove_line(self):
        for l in self.line:
            self.graph.canvas.remove(l)

        self.line = []
        self.data = []

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
                self.parent.remove_line()
        return True

    def insert_text(self, substring, from_undo=False):
        s = substring.lower()
        if not s.isspace():
            return super(EquationInput, self).insert_text(s, from_undo=from_undo)
