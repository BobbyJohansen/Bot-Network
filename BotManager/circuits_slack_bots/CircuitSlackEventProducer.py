from circuits import BaseComponent, Component
from circuits.tools import graph

from log.logger import Logger


class CircuitSlackEventProducer(Component):
    def __init__(self):
        super(CircuitSlackEventProducer, self).__init__()
        self._bot_listeners = []
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    # This is a private method so that the auto decorators stay away from it
    def _register_listeners(self, consumers):
        for consumer in consumers:
            self._bot_listeners.append(consumer().register(self))

    def started(self, *args):
        self._logger.info("Starting Event Producer Framework")
        self._logger.info(graph(self.root))