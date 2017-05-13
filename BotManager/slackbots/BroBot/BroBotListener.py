from circuits import BaseComponent, Component

from log.logger import Logger


class BroBotListener(Component):
    def __init__(self):
        super(BroBotListener, self).__init__()
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def message(self):
        self._logger.info("Received Message In listener")
