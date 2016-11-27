from threading import Thread

import time
from circuits import BaseComponent

from log.logger import Logger
from slackbots.BroBot import BroBotListener
from slackbots.SlackListener import SlackListener


class BroBot(Thread):
    def __init__(self, bot_info, managerQ, qlock, heart_beat_interval):
        super(BroBot, self).__init__(name="BroBot")
        self._slack_listener = SlackListener("brobot", bot_info, managerQ,
                                             qlock, BroBotListener.BroBotListener, heart_beat_interval)
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def init(self):
        self._slack_listener.init()
        # TODO daemon?
        self._slack_listener.start()

    def run(self):
        while True:
            # This is where we run any logic outside of event driven framework
            self._logger.info("Bot loop running")
            time.sleep(10)