import time
from threading import Thread

from slackclient import SlackClient
from circuits import BaseComponent, Component
from BotHeart import BotHeart

from log.logger import Logger

from circuits_slack_bots.CircuitSlackEventProducer import CircuitSlackEventProducer
from circuits_slack_bots.circuit_events.event_map import slack_event_map


class CircuitSlackListener(Thread):
    def __init__(self, bot_type, bot_info, managerQ, qlock, heart_beat_interval=10):
        name = "slackbot_" + str(bot_type) + "_" + str(bot_info['team_name'])
        super(CircuitSlackListener, self).__init__(name=name)
        self._bot_type = bot_type
        self._bot_heart = BotHeart(name, managerQ, qlock, heart_beat_interval)

        self._token = bot_info['bot_access_token']
        self._team_name = bot_info['team_name']
        self._sc = None
        self._users = None
        self._event_map = slack_event_map

        # create event producer (will need to register event listeners to it to receive its events)
        self._event_producer = CircuitSlackEventProducer()

        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def __str__(self):
        return "slackbot_" + str(self._bot_type) + "_" + str(self._team_name)

    def init(self, listeners=None):
        self._logger.info(str(self) + "Starting bot setup...")
        if listeners == None: self._logger.warn("Heads up you wont receive events with no listener")
        # register bot listeners and start component for events
        self._event_producer._register_listeners(listeners)
        self._event_producer.start()

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

    # Override Thread.run
    def run(self):
        # run main bot loop
        self._run_slack_listener()

    def _run_slack_listener(self):
        self._logger.info(str(self) + "Starting bot loop...")
        while True:
            self._retrieve_and_process_messages()
            time.sleep(1)

    def _retrieve_and_process_messages(self):
        events = self._sc.rtm_read()
        for event in events:
            self._logger.info("Event Received: " + event.get("type"))
            self._dispatch_event(event)
            # TODO dispatch events to overriden methods

    def _dispatch_event(self, event):
        event_type = event.get("type")
        if(event_type in self._event_map):
            event = self._event_map[event_type]
            # TODO: add event data to the event
            self._event_producer.fire(event())
        else:
            self._logger.info("Event of type " + event_type + " not handled ignoring it.")

            ################ Actions that can be performed ############################################

    def send_message_rtm(self, channel, message):
        """ Only supports basic formatting, does not support attachments
            for other formatting use the send via api """
        self._sc.rtm_send_message(channel, message)


def send_basic_message_api(self, channel, message):
    self._sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

def update_basic_message_api(self, ts, channel, updated_message):
    self._sc.api_call(
        "chat.update",
        ts=ts,
        channel=channel,
        text=updated_message
    )

def delete_basic_message_api(self, ts, channel):
    self._sc.api_call(
        "chat.delete",
        channel=channel,
        ts=ts
    )
