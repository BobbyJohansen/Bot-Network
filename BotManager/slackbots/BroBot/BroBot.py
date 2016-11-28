from threading import Thread

import time
from circuits import BaseComponent

from log.logger import Logger
from slackbots.BroBot import BroBotListener
from slackbots.SlackBot import SlackBot


class BroBot(SlackBot):
    def __init__(self, bot_info, managerQ, qlock, heart_beat_interval):
        super(BroBot, self).__init__("brobot", bot_info, managerQ, qlock, heart_beat_interval)
        self._bro_bot_loop = Thread() # main thread for running any bot specific tasks
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def setup_bot(self):
        pass

    def message_event(self, event):
        self._logger.info("message in bro bot")
