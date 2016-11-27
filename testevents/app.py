from threading import Thread

import time

from testevents.EventProducer import EventProducer


class App(Thread):
    def __init__(self):
        super(App, self).__init__(name="App")
        self._producer = EventProducer()

    def dispatch(self):
        self._producer.produce()

    def run(self):
        while True:
            self.dispatch()
            time.sleep(2)

if __name__ == "__main__":
    app = App()
    app.start()