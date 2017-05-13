from threading import Thread

import time

from testevents.EventConsumer import EventConsumer
from testevents.EventProducer import EventProducer

from testevents.produced import produced


class App(Thread):
    def __init__(self):
        super(App, self).__init__(name="App")
        self._consumer = EventConsumer
        self._producer = EventProducer(self._consumer)
        self._producer.start()

    def dispatch(self):
        self._producer.fire(produced())

    def run(self):
        while True:
            self.dispatch()
            time.sleep(2)

if __name__ == "__main__":
    app = App()
    app.start()