from circuits import BaseComponent, Component

from log.logger import Logger


class CircuitBroBotEventListener(Component):
    def __init__(self, api):
        super(CircuitBroBotEventListener, self).__init__()
        self._api = api
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def message_event(self, message):
        self._logger.info("Received Message In listener CircuitBroBotEventListener")
        self._api.send_message_rtm(message['channel'], "bye")
        # self._api.get_channel_history_api(message['channel'])

    def sys_response_event(self, message):
        self._logger.info("Received Response event")
