"""
This manages a set amount of processes (bots) running on this system.
"""
from concurrent.futures import ProcessPoolExecutor
from threading import Thread

import time

from log.logger import Logger


class BotManager(Thread):
    def __init__(self, name, command_queue, qlock, max_workers):
        super(BotManager, self).__init__(name=name)
        # self._name = name
        self._command_queue = command_queue
        self._qlock = qlock
        self._bots = {}
        self._executor = ProcessPoolExecutor(max_workers=max_workers)
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def init(self):
        self._logger.info("Initializing Bot Manager")


    # Override Thread.run
    def run(self):
        self._logger.info("Bot Manager at your service")
        self._logger.info("Ready Executor")
        self._logger.info("For Aiur!")
        # Run main loop
        while True:
            self._check_bots()

            # check queue for new bots to deploy
            with self._qlock:
                if not self._command_queue.empty():
                    bot_info = self._command_queue.get()
                    self._logger.info("Received New Bot To deploy")
                    self._logger.info(bot_info)
                    self._deploy(bot_info)

            self._logger.info("Bot Manager Alive")
            time.sleep(10)

    def _deploy(self, bot_info):
        state = "bro" #TODO: get state fromm bot_info
        self._logger.info("Deploying bot of type " + state)

    def _check_bots(self):
        # TODO: get status of bots maybe through REST again so that Bots know how to define their status or through a Queue
        # TODO: if a bot goes down notify Command Listener?????
        self._logger.info("checking status of all bots under Bot Manager")
        self._logger.info("bots: " + str(self._bots))
