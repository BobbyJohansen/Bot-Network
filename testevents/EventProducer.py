import time
from circuits import Component, Event, BaseComponent
from circuits.tools import graph


class EventProducer(Component):
    def __init__(self, component):
        super(EventProducer, self).__init__()
        self.consumer = component().register(self)

    def started(self, *args):
        print(graph(self.root))