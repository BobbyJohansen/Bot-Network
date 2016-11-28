import time
from threading import Thread

from slackclient import SlackClient
from circuits import BaseComponent, Component
from BotHeart import BotHeart

from log.logger import Logger


class SlackBot(Thread):
    def __init__(self, bot_type, bot_info, managerQ, qlock, heart_beat_interval=10):
        name = "slackbot_" + str(bot_type) + "_" + str(bot_info['team_name'])
        super(SlackBot, self).__init__(name=name)
        self._bot_type = bot_type
        self._bot_heart = BotHeart(name, managerQ, qlock, heart_beat_interval)

        self._token = bot_info['bot_access_token']
        self._team_name = bot_info['team_name']
        self._sc = None
        self._users = None

        self._event_handlers = {
            "message": self.message_event,
            "reconnect_url": self.reconnect_url_event,
            "presence_change": self.presence_change_event,
            # hello - successfully connected with client
            "hello": self.hello_connection_event,
            "user_typing": self.user_typing_event,
            "user_change": self.user_change_event,
            "team_rename": self.team_rename_event,
            "team_profile_reorder": self.team_profile_reorder_event,
            "team_profile_delete": self.team_profile_delete_event,
            "team_profile_change": self.team_profile_change_event,
            "team_pref_change": self.team_pref_change,
            "team_plan_change": self.team_plan_change_event,
            "team_migration_started": self.team_plan_change_event,
            "team_join": self.team_join_event,
            "team_domain_change_event": self.team_domain_change_event,
            "subteam_updated": self.subteam_updated_event,
            "subteam_self_removed": self.subteam_self_removed_event,
            "subteam_self_added": self.subteam_self_added_event,
            "subteam_created": self.subteam_created_event,
            "star_removed": self.star_removed_event,
            "star_added": self.star_added_event,
            "reaction_removed": self.reaction_removed_event,
            "reaction_added": self.reaction_added_event,
            "pref_change": self.pref_change_event,
            "pin_removed": self.pin_removed_event,
            "pin_added": self.pin_added_event,
            "manual_presence_change": self.manual_presence_change_event,
            "im_open": self.im_open_event,
            "im_marked": self.im_marked_event,
            "im_history_changed": self.im_history_changed_event,
            "im_created": self.im_create_event,
            "im_close": self.im_close_event,
            "group_unarchive": self.group_unarchive_event,
            "group_rename": self.group_rename_event,
            "group_open": self.group_open_event,
            "group_marked": self.group_marked_event,
            "group_left": self.group_left_event,
            "group_joined": self.group_joined_event,
            "group_history_changed": self.group_history_changed_event,
            "group_close": self.group_close_event,
            "group_archive": self.group_archive_event,
            # goodbye - server intends to close the connection soon
            "goodbye": self.goodbye_event,
            "file_unshared_event": self.file_unshared_event,
            "file_shared": self.file_shared_event,
            "file_public": self.file_public_event,
            "file_deleted": self.file_deleted_event,
            "file_created": self.file_created_event,
            "file_comment_edited": self.file_comment_edited_event,
            "file_comment_deleted": self.file_comment_deleted_event,
            "file_comment_added": self.file_comment_added_event,
            "file_change": self.file_change_event,
            "emoji_changed": self.emoji_changed_event,
            "email_domain_changed": self.email_domain_changed,
            "dnd_updated_user": self.dnd_updated_user_event,
            "dnd_updated": self.dnd_updated_event,
            "commands_changed": self.commands_changed_event,
            "channel_unarchive": self.channel_unarchive_event,
            "channel_rename": self.channel_rename_event,
            "channel_marked": self.channel_marked_event,
            "channel_left": self.channel_left_event,
            "channel_joined": self.channel_joined_event,
            "channel_history_changed": self.channel_history_changed_event,
            "channel_deleted": self.channel_deleted_event,
            "channel_created": self.channel_created_event,
            "channel_archive": self.channel_archive_event,
            "bot_changed": self.bot_changed_event,
            "bot_added": self.bot_added_event,
            "accounts_changed": self.accounts_changed_event
        }
        self._logger = Logger().gimme_logger(self.__class__.__name__)

    def __str__(self):
        return "slackbot_" + str(self._bot_type) + "_" + str(self._team_name)

    def init(self, bot_component=None):
        self._logger.info(str(self) + "Starting bot setup...")

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
        if(event_type in self._event_handlers):
            event_handler = self._event_handlers[event_type]
            event_handler(event)
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

    ######################################################################
    #########   Override These in order to listen for the events in Bot ##
    ######################################################################
    def hello_connection_event(self, event):
        self._logger.info("Successfully connected Bot: " + str(self))

    def goodbye_event(self, event):
        self._logger.warn("Server intends to disconnect client Bot: " + str(self))
        self._logger.warn("Unless the bot is okay to die off, you may want to refresh the connection")

    def reconnect_url_event(self, event):
        pass

    def user_typing_event(self, event):
        pass

    def message_event(self, event):
        pass

    def presence_change_event(self, event):
        pass

    def user_change_event(self, event):
        pass

    def team_rename_event(self, event):
        pass

    def team_profile_reorder_event(self, event):
        pass

    def team_profile_delete_event(self, event):
        pass

    def team_profile_change_event(self, event):
        pass

    def team_pref_change(self, event):
        pass

    def team_plan_change_event(self, event):
        pass

    def team_plan_change_event(self, event):
        pass

    def team_join_event(self, event):
        pass

    def team_domain_change_event(self, event):
        pass

    def subteam_updated_event(self, event):
        pass

    def subteam_self_removed_event(self, event):
        pass

    def subteam_self_added_event(self, event):
        pass

    def subteam_created_event(self, event):
        pass

    def star_removed_event(self, event):
        pass

    def star_added_event(self, event):
        pass

    def reaction_removed_event(self, event):
        pass

    def reaction_added_event(self, event):
        pass

    def pref_change_event(self, event):
        pass

    def pin_removed_event(self, event):
        pass

    def pin_added_event(self, event):
        pass

    def manual_presence_change_event(self, event):
        pass

    def im_open_event(self, event):
        pass

    def im_marked_event(self, event):
        pass

    def im_history_changed_event(self, event):
        pass

    def im_create_event(self, event):
        pass

    def im_close_event(self, event):
        pass

    def group_unarchive_event(self, event):
        pass

    def group_rename_event(self, event):
        pass

    def group_open_event(self, event):
        pass

    def group_marked_event(self, event):
        pass

    def group_left_event(self, event):
        pass

    def group_joined_event(self, event):
        pass

    def group_history_changed_event(self, event):
        pass

    def group_close_event(self, event):
        pass

    def group_archive_event(self, event):
        pass

    def file_unshared_event(self, event):
        pass

    def file_shared_event(self, event):
        pass

    def file_public_event(self, event):
        pass

    def file_deleted_event(self, event):
        pass

    def file_created_event(self, event):
        pass

    def file_comment_edited_event(self, event):
        pass

    def file_comment_deleted_event(self, event):
        pass

    def file_comment_added_event(self, event):
        pass

    def file_change_event(self, event):
        pass

    def emoji_changed_event(self, event):
        pass

    def email_domain_changed(self, event):
        pass

    def dnd_updated_user_event(self, event):
        pass

    def dnd_updated_event(self, event):
        pass

    def commands_changed_event(self, event):
        pass

    def channel_unarchive_event(self, event):
        pass

    def channel_rename_event(self, event):
        pass

    def channel_marked_event(self, event):
        pass

    def channel_left_event(self, event):
        pass

    def channel_joined_event(self, event):
        pass

    def channel_history_changed_event(self, event):
        pass

    def channel_deleted_event(self, event):
        pass

    def channel_created_event(self, event):
        pass

    def channel_archive_event(self, event):
        pass

    def bot_changed_event(self, event):
        pass

    def bot_added_event(self, event):
        pass

    def accounts_changed_event(self, event):
        pass