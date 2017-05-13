from threading import Thread

import time

from log.logger import Logger


class BotHeart(Thread):
    def __init__(self, name, managerQ, qlock, heart_beat_interval):
        super(BotHeart, self).__init__(name=name)
        self._managerQ = managerQ
        self._qlock = qlock
        self._heart_beat_interval = heart_beat_interval
        self._state = 'running'
        self._logger = Logger().gimme_logger(self.__class__.__name__)

        # Override Thread.run
    def run(self):
        # run main bot loop
        self._send_heart_beat()
        time.sleep(self._heart_beat_interval)

    def set_state(self, state):
        self._state = state

    def _send_heart_beat(self):
        with self._qlock:
            self._managerQ.put(self._state)
