from circuits import BaseComponent, Component

from log.logger import Logger
from slackbots.on_message import message


class BotNotifier(Component):
    def __init__(self, listener):
        super(BotNotifier, self).__init__()
        self._bot_listener = listener().register(self)
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def message_found(self):
        self._logger.info("Bot NOtifier message found")
        self.fire(message())