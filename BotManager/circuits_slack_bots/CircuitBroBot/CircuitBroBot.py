from threading import Thread

import time
from circuits import BaseComponent

from log.logger import Logger

from circuits_slack_bots.CircuitBroBot.CircuitBroBotEventListener import CircuitBroBotEventListener
from circuits_slack_bots.CircuitSlackListener import CircuitSlackListener
from slackbots.BroBot import BroBotListener
from slackbots.SlackBot import SlackBot


class CircuitBroBot(Thread):
    def __init__(self, bot_info, managerQ, qlock, heart_beat_interval):
        super(CircuitBroBot, self).__init__(name="brobot")

        # This is the slack listener we must initialize it and register our bot to it and start it
        self._slack_listener = CircuitSlackListener("brobot", bot_info, managerQ, qlock, heart_beat_interval)
        self._event_listener = CircuitBroBotEventListener
        self._slack_listener.init([CircuitBroBotEventListener])
        self._slack_listener.start()

        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def init(self):
        pass

    def run(self):
        while True:
            self._logger.info("In Main CircuitBot loop")
            time.sleep(10)

