from circuits_slack_bots.circuit_events.message_event import message_event

slack_event_map = {
    "message": message_event
    # "reconnect_url": reconnect_url_event,
    # "presence_change": presence_change_event,
    # # hello - successfully connected with client
    # "hello": hello_connection_event,
    # "user_typing": user_typing_event,
    # "user_change": user_change_event,
    # "team_rename": team_rename_event,
    # "team_profile_reorder": team_profile_reorder_event,
    # "team_profile_delete": team_profile_delete_event,
    # "team_profile_change": team_profile_change_event,
    # "team_pref_change": team_pref_change,
    # "team_plan_change": team_plan_change_event,
    # "team_migration_started": team_plan_change_event,
    # "team_join": team_join_event,
    # "team_domain_change_event": team_domain_change_event,
    # "subteam_updated": subteam_updated_event,
    # "subteam__removed": subteam__removed_event,
    # "subteam__added": subteam__added_event,
    # "subteam_created": subteam_created_event,
    # "star_removed": star_removed_event,
    # "star_added": star_added_event,
    # "reaction_removed": reaction_removed_event,
    # "reaction_added": reaction_added_event,
    # "pref_change": pref_change_event,
    # "pin_removed": pin_removed_event,
    # "pin_added": pin_added_event,
    # "manual_presence_change": manual_presence_change_event,
    # "im_open": im_open_event,
    # "im_marked": im_marked_event,
    # "im_history_changed": im_history_changed_event,
    # "im_created": im_create_event,
    # "im_close": im_close_event,
    # "group_unarchive": group_unarchive_event,
    # "group_rename": group_rename_event,
    # "group_open": group_open_event,
    # "group_marked": group_marked_event,
    # "group_left": group_left_event,
    # "group_joined": group_joined_event,
    # "group_history_changed": group_history_changed_event,
    # "group_close": group_close_event,
    # "group_archive": group_archive_event,
    # # goodbye - server intends to close the connection soon
    # "goodbye": goodbye_event,
    # "file_unshared_event": file_unshared_event,
    # "file_shared": file_shared_event,
    # "file_public": file_public_event,
    # "file_deleted": file_deleted_event,
    # "file_created": file_created_event,
    # "file_comment_edited": file_comment_edited_event,
    # "file_comment_deleted": file_comment_deleted_event,
    # "file_comment_added": file_comment_added_event,
    # "file_change": file_change_event,
    # "emoji_changed": emoji_changed_event,
    # "email_domain_changed": email_domain_changed,
    # "dnd_updated_user": dnd_updated_user_event,
    # "dnd_updated": dnd_updated_event,
    # "commands_changed": commands_changed_event,
    # "channel_unarchive": channel_unarchive_event,
    # "channel_rename": channel_rename_event,
    # "channel_marked": channel_marked_event,
    # "channel_left": channel_left_event,
    # "channel_joined": channel_joined_event,
    # "channel_history_changed": channel_history_changed_event,
    # "channel_deleted": channel_deleted_event,
    # "channel_created": channel_created_event,
    # "channel_archive": channel_archive_event,
    # "bot_changed": bot_changed_event,
    # "bot_added": bot_added_event,
    # "accounts_changed": accounts_changed_event
}