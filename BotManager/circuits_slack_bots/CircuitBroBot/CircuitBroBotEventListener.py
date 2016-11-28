from circuits import BaseComponent, Component

from log.logger import Logger


class CircuitBroBotEventListener(Component):
    def __init__(self):
        super(CircuitBroBotEventListener, self).__init__()
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def message_event(self):
        self._logger.info("Received Message In listener CircuitBroBotEventListener")
