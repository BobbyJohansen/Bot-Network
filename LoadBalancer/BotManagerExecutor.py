"""
This balances bot placement to bot managers on a round robin
Talks to bot managers over some network protocol
"""
import os
from threading import Thread

import requests

from log.logger import Logger
import rethinkdb as r


class BotManagerExecutor(Thread):
    def __init__(self, name, auth_queue, qlock, managers, creation_endpoint):
        super(BotManagerExecutor, self).__init__(name=name)
        # self._name = name
        self._managers = managers
        self._creation_endpoint = creation_endpoint
        self._next_manager = 0
        self._auth_queue = auth_queue
        self._qlock = qlock
        self._db_conn = None
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def init(self):
        self._logger.info("Initializing Bot Manager Executor")
        db_host = os.environ["RETHINK_HOST"]
        db_port = os.environ["RETHINK_PORT"]
        db_name = os.environ["RETHINK_DB"]
        db_user = os.environ["RETHINK_USER"]
        db_password = os.environ["RETHINK_PASSWORD"]
        self._logger.info("Initializing Database Connection")
        self._db_conn = r.connect(host=db_host, port=db_port, db=db_name, user=db_user, password=db_password).repl()

    def run(self):
        # say hi
        self._logger.info("Yes Executor?!")
        self._logger.info("Awaiting your command!")

        # Load the existing bots already in the database and run them
        self._load_run_existing_bots()

        while True:
            # Grab the lock for the queue
            with self._qlock:
                # Listen on queue and check if we get anything
                if not self._auth_queue.empty():
                    auth_message = self._auth_queue.get()
                    self._logger.info("Recieved New Authentication Message")
                    self._logger.info(auth_message)

                    # Save or Update the bot
                    bot_info = self._save_or_update_bot(auth_message)

                    # Time to create a new bot, send it to a single distributed bot manager
                    if bot_info is not None:
                        self._run_bot(bot_info)

    # persist the bot to the db so we can load it later
    def _save_or_update_bot(self, bot):
        self._logger.info("persisting bot")
        # TODO not sure about recycling authentication here probably should kill the bot and take the new token
        try:
            # If the bot exists already, update the token and run the bot. It is possible the other one was removed or died
            cursor = r.table('accounts').filter((r.row["bot_info"]['team_name'] == bot['team_name']) &
                                                (r.row["bot_info"]["bot_type"] == bot['state']) &
                                                (r.row["bot_info"]["channel_type"] == bot['channel_type'])).run(self._db_conn)

            count = r.table('accounts').filter((r.row["bot_info"]["team_name"] == bot['team_name']) &
                                               (r.row["bot_info"]["bot_type"] == bot['state']) &
                                               (r.row["bot_info"]["channel_type"] == bot['channel_type'])).without('id').distinct().count().run(self._db_conn)

            self._logger.info("Found count of documents: " + str(count))
            # else save a new entry for the bot and return anything needed to run the bot
            documents = list(cursor)
            if len(documents) == 0:
                # save and return
                # TODO: make this a class with a generate dictionary?
                new_bot = {'bot_info': {
                    'team_name': bot['team_name'],
                    'team_id': bot['team_id'],
                    'bot_type': bot['state'],
                    'channel_type': bot['channel_type'],
                    'user_access_token': bot['user_access_token'],
                    'bot_access_token': bot['bot_access_token'],
                    'trashed_tokens': [],
                    'installer_id': bot['user_id']},
                    'created': r.now(),
                    'updated': r.now(),
                    'expired': False,
                    'internal': False,
                    'poc_email': "",
                    'poc_phone': "",
                    'paid': False,
                    'paid_for': "forever",
                    'trial': False}
                try:
                    r.table('accounts').insert(new_bot).run(self._db_conn)
                    return new_bot
                except Exception as e:
                    self._logger.error("Failed to insert new bot")
                    self._logger.error(e)

            else:
                self._logger.info("Found " + str(len(documents)) + " documents for bot")
                # update and return
                try:
                    trashed_tokens = documents[0]["bot_info"]['trashed_tokens']
                    trashed_tokens.append(documents[0]["bot_info"]['bot_access_token'])
                    r.table('accounts').get(documents[0]['id']).update({'bot_info':{'trashed_tokens': trashed_tokens,
                                                                        'bot_access_token': bot['bot_access_token']},
                                                                        'updated': r.now()}).run(self._db_conn)
                    updated_doc = r.table('accounts').get(documents[0]['id']).run(self._db_conn)
                    if updated_doc is None:
                        self._logger.error("Update document is now None? Uhoh where did it go???")
                    return updated_doc
                except Exception as e:
                    self._logger.error("Failed to update bot after being found")
                    self._logger.error(e)

        except Exception as e:
            self._logger.error("Failed to check/save db for bot " + str(bot))
            self._logger.error(e)

        return None

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
            self._logger.info("Response from dispatch to: " + manager + " is " + str(response))
        except Exception as e:
            self._logger.error("Failed to dispatch bot to manager: " + str(manager))
            self._logger.error(e)

            # TODO: also need a personal token for security and check on the other side

    # Load up the already authed bots and run them placing them across all Bot Managers
    def _load_run_existing_bots(self):
        existing_bots = []
        # TODO: grab them from the database and return them
        self._logger.info("Retrieving already authenticated bots from our bots repo")
        cursor = r.table('accounts').run(self._db_conn)
        for account in cursor:
            self._logger.info("Starting bot for account: " + account['bot_info']['team_name'])
            self._run_bot(account)

    def _get_next_manager(self):
        if (len(self._managers) - 1) < self._next_manager:
            self._next_manager = 0
            return self._get_next_manager()
        # TODO: if manager is out of resources move to the next manager
        # TODO after moving to the next based on resources identitfy we hit infinite loop after 1 iteration and notify
        manager = self._managers[self._next_manager]
        self._next_manager += 1
        return manager

    def _get_resources_for_manager(self, manager):
        try:
            # Call rest endpoint for bot manager from env managers for resources
            self._logger.info("Attempting to dispatch to: " + manager)
            response = requests.get(manager + '/resources')
            self._logger.info("Response of resources from: " + manager + " is " + response)
            return response
        except Exception as e:
            self._logger.error("Failed to retrieve bot manager resources from: " + manager)
            self._logger.error(e)
