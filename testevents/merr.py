from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import time
from circuits import Component, Event
from circuits.tools import graph

class pew(Event):
    """Event Pew"""


class Pound(Component):

    def __init__(self):
        super(Pound, self).__init__()

        self.bob = Bob().register(self)
        self.fred = Fred().register(self)

    def started(self, *args):
        print(graph(self.root))

    def myfire(self):
        self.fire(pew())

    def run(self):
        super().run()
        while True:
            print("running")
            self.myfire()
            time.sleep(10)


class Bob(Component):

    def started(self, *args):
        print("Hello I'm Bob!")

    def pew(self, *args):
        print("pew Bob")


class Fred(Component):

    def started(self, *args):
        print("Hello I'm Fred!")

    def pew(self, *args):
        print("pew Fred")


Pound().run()
