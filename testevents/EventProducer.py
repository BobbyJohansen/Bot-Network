from circuits import Component

from testevents.EventConsumer import EventConsumer
from testevents.produced import produced


class EventProducer(Component):
    def __init__(self):
        super(EventProducer, self).__init__()
        self._consumers = [
            EventConsumer().start(process=True, link=self)
        ]


    def produce(self):
        print("EventProducer: produce called")
        self.fire(produced())