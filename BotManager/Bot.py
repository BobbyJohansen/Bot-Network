from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import time

from log.logger import Logger


class Bot(Thread):
    def __init__(self, name, type, token):
        super(Bot, self).__init__(name=name)
        self._team_name = ""
        self._manager_id = ""

        self._type = type
        self._token = token
        self._executor = ThreadPoolExecutor(max_workers=5)
        # TODO: getting a new Logger class everytime should be a singleton look up how to do this in python
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def init(self):
        self._logger.info("Initiating Bot Startup")

    #Override Thread.run
    def run(self):
        # setup bot and attach to chat client
        self._setupBot()
        # run main bot loop
        self._runBotLoop()

    def _setupBot(self):
        # Add listeners and anything needed to receive messages from chat client
        pass;

    def _runBotLoop(self):
        with self._executor as executor:
            while True:
                # slack listen for messages
                self._logger.info("Polling for Message")
                time.sleep(5)