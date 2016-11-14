"""
This balances bot placement to bot managers on a round robin
Talks to bot managers over some network protocol
"""
from threading import Thread

import flask
import requests

from log.logger import Logger


class BotManagerExecutor(Thread):
    def __init__(self, name, auth_queue, qlock, managers, creation_endpoint):
        super(BotManagerExecutor, self).__init__(name=name)
        # self._name = name
        self._managers = managers
        self._creation_endpoint = creation_endpoint
        self._next_manager = 0
        self._auth_queue = auth_queue
        self._qlock = qlock
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def init(self):
        self._logger.info("Initializing Bot Manager Executor")

    def run(self):
        # say hi
        self._logger.info("Yes Executor?!")
        self._logger.info("Awaiting your command!")

        # Load the existing bots already in the database and run them
        existing_bots = self._load_existing_bots()
        for bot in existing_bots:
            self._run_bot(bot)

        while True:
            # Grab the lock for the queue
            with self._qlock:
                # Listen on queue and check if we get anything
                if not self._auth_queue.empty():
                    auth_message = self._auth_queue.get()
                    self._logger.info("Recieved New Authentication Message")
                    self._logger.info(auth_message)

                    # Save or Update the bot
                    bot_info = self._save_bot(auth_message)

                    # Time to create a new bot, send it to a single distributed bot manager
                    self._run_bot(bot_info)


    # persist the bot to the db so we can load it later
    def _save_bot(self, bot):
        self._logger.info("TODO: persisitng bot")
        # If the bot exists by id then grab it and run it
        # else save a new entry for the bot and return anything needed to run the bot
        return bot


    # Create a new bot if it does not exist already should be moved into a bot manager
    # message will be dict {state:w, team_name:x, bot_access_token:y, user_access_token:z}
    def _run_bot(self, bot_info):
        self._logger.info("Dispatching bot creation process to a Bot manager via REST")

        try:
            # Get the next manager to dispatch to
            manager = self._get_next_manager()

            # Call rest endpoint for bot manager from env managers
            self._logger.info("Attempting to dispatch to: " + manager)
            response = requests.post(manager + self._creation_endpoint, params=bot_info)
            self._logger.info("Response from dispatch to: " + manager + " is " + response)
        except Exception as e:
            self._logger.error("Failed to dispatch bot to manager: " + manager)
            self._logger.error(e)

        # TODO: call rest endpoints on bot managers requests POST with bot_info=auth_message passed
        # TODO: also need a personal token for security and check on the other side

    # Load up the already authed bots and run them placing them across all Bot Managers
    def _load_existing_bots(self):
        existing_bots = []
        # TODO: grab them from the database and return them
        self._logger.info("TODO: Starting up already authenticated bots from our bots repo")
        return existing_bots

    def _get_next_manager(self):
        if (len(self._managers) - 1) < self._next_manager:
            self._next_manager = 0
            return self._get_next_manager()
        manager = self._managers[self._next_manager]
        self._next_manager += 1
        return manager



