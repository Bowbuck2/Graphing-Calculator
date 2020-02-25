from random import randrange

from kivy.clock import Clock
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
            self.data.append(EquationInput(position=self.data[-1].get('position') + 1, ctx=self).__dict__())

    def update_position(self):
        """
        Updates Positions after Labels are Removed
        """
        for count,data in enumerate(self.data):
            data['position'] = count

    def init_gen(self, dt):
        """
        on app start, will generate EquationInput
        """
        for amount in range(0, 1):
            equation_input = EquationInput(position=amount, ctx=self)
            self.data.append(equation_input.__dict__())


class EquationInput(FloatLayout):
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

    def update_equation(self, equation_text):
        """
        updates RV data of equation input
        checks if equation is a function
        """
        for data in self.ctx.data:
            if data['position'] == self.position:
                data['equation'] = equation_text




    def remove_equation(self):
        """
        Removes Self
        """
        self.ctx.data.pop(self.position)
        self.ctx.update_position()

    def __dict__(self):
        return self.dat


class TI(TextInput):

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
            return super(TI, self).insert_text(s, from_undo=from_undo)
