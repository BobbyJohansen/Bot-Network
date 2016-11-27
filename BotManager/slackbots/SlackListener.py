import time
from threading import Thread

from slackclient import SlackClient
from circuits import BaseComponent, Component
from BotHeart import BotHeart

from log.logger import Logger
from slackbots.BotNotifier import BotNotifier


class SlackListener(Thread):

    def __init__(self, bot_type, bot_info, managerQ, qlock, listener, heart_beat_interval=10):
        name = "slackbot_" + str(bot_type) + "_" + str(bot_info['team_name'])
        super(SlackListener, self).__init__(name=name)
        self._bot_type = bot_type
        self._token = bot_info['bot_access_token']
        self._team_name = bot_info['team_name']

        self._slack_notifier = BotNotifier(listener)

        self._sc = None
        self._users = None
        self._bot_heart = BotHeart(name, managerQ, qlock, heart_beat_interval)
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def __str__(self):
        return "slackbot_" + str(self._bot_type) + "_" + str(self._team_name)

    def init(self, bot_component=None):
        self._logger.info(str(self) + "Starting bot setup...")

        # start the notifier
        self._slack_notifier.run()

        # start the heart beat
        self._bot_heart.start() # TODO set daemon?

        # start the slack connection
        self._sc = SlackClient(self._token)
        try:
            if self._sc.rtm_connect():
                self._users = self._sc.server.users
            else:
                self._logger.error("Failed to Connect to slack for unknown reason")
            # self._register_components(bot_component)
        except Exception as e:
            self._logger.error("Failed to connect to slack... ")
            self._logger.error(e)

    def _register_components(self, bot_component):
        if bot_component is not None:
            self._complex_component.register(bot_component)
        else:
            self._logger.warn("Bot component is None")

    # Override Thread.run
    def run(self):
        # run main bot loop
        self._run_slack_listener()

    def _run_slack_listener(self):
        self._logger.info(str(self) + "Starting bot loop...")
        while True:
            self._get_message()

    def _get_message(self):
        events = self._sc.rtm_read()
        for event in events:
            self._logger.info("Event Received: " + event.get("type"))
            # TODO dispatch event to complex component
            self._slack_notifier.message_found()
        time.sleep(1)

    def _send_message(self, channel, message):
        self._sc.rtm_send_message(channel, message)