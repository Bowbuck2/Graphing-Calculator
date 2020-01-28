import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.widget import Widget

from random import randint as ran

import matplotlib

matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
import matplotlib.pyplot as plt


class Main(FloatLayout):
    pass


fig, ax = plt.subplots()
canvas = fig.canvas


class Graph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fig, self.ax = plt.subplots(1)
        self.plt_canvas = self.fig.canvas
        self.add_widget(self.plt_canvas)

        self.line = self.ax.plot([])[0]
        self.i = 0
        plt.show()
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        self.line.set_xdata(np.arange(self.i))
        self.line.set_ydata(np.arange(self.i))
        self.i += 1

        plt.draw()


class SideBar(FloatLayout):
    pass


class InputField(RecycleView):
    pass


class WidgetColor(Widget):
    r = NumericProperty()
    g = NumericProperty()
    b = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.r = ran(0, 255) / 255
        self.g = ran(0, 255) / 255
        self.b = ran(0, 255) / 255


class MyApp(App):
    def build(self):
        return Main()
