from kivy.app import App
from kivy.uix.floatlayout import FloatLayout


class Main(FloatLayout):
    pass


class MyApp(App):
    def build(self):
        return Main()


if __name__ == '__main__':
    MyApp().run()
