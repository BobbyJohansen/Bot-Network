"""
This manages a set amount of processes (bots) running on this system.
"""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import Thread

import time
from multiprocessing import Queue
from multiprocessing import Lock

from circuits_slack_bots.CircuitBroBot import CircuitBroBot
from slackbots.BroBot import BroBot
from log.logger import Logger


class BotManager(Thread):
    def __init__(self, name, command_queue, qlock):
        super(BotManager, self).__init__(name=name)
        # self._name = name
        self._command_queue = command_queue
        self._qlock = qlock
        self._bots = []
        self._polling_time = 10
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
            # Check status of existing bots
            self._check_bots()

            # check queue for new slackbots to deploy
            with self._qlock:
                if not self._command_queue.empty():
                    bot_info = self._command_queue.get()
                    self._logger.info("Received New Bot To deploy")
                    self._logger.info(bot_info)
                    self._deploy(bot_info)

            # inform we are alive
            self._logger.info("Bot Manager Alive")
            time.sleep(self._polling_time)

    def _deploy(self, bot_info):
        managerQ = Queue()
        qlock = Lock()
        bot_type = bot_info['bot_type']
        bot_class = self._get_bot_from_type(bot_type)
        bot = bot_class(bot_info, managerQ, qlock, self._polling_time)
        self._logger.info("Deploying bot of type " + bot_type)
        bot.init()
        self._bots.append({'managerQ': managerQ, 'qlock': qlock, 'bot': bot, 'status':'running'})
        bot.setDaemon(True)
        bot.start()

    def _get_bot_from_type(self, type):
        return CircuitBroBot.CircuitBroBot

    def _check_bots(self):
        # TODO: get status of slackbots maybe through REST again so that Bots know how to define their status or through a Queue
        # TODO: if a bot goes down notify Command Listener?????
        self._logger.info("checking status of all slackbots under Bot Manager")
        for bot in self._bots:
            managerQ = bot['managerQ']
            status = "running"
            with bot['qlock'] as lock:
                while not managerQ.empty():
                    status = managerQ.get()
                bot['status'] = status
                self._logger.info(str(bot['bot']) + " status: " + status)


