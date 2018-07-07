# | Created by Ar4ikov
# | Время: 06.07.2018 - 12:50
from enum import Enum

from vk_advanced_api.event_types import Message, Act, Attachments, Join, Leave, CallbackEvent


class DataTypes(Enum):
    CONFIRMATION = "confirmation"

    MESSAGE_NEW = "message_new"
    MESSAGE_REPLY = "message_reply"
    MESSAGE_EDIT = "message_edit"
    MESSAGE_ALLOW = "message_allow"
    MESSAGE_DENY = "message_deny"
    MESSAGE_TYPING_STATE = "message_typing_state"

    PHOTO_NEW = "photo_new"
    PHOTO_COMMENT_NEW = "photo_comment_new"
    PHOTO_COMMENT_EDIT = "photo_comment_edit"
    PHOTO_COMMENT_DELETE = "photo_comment_delete"
    PHOTO_COMMENT_RESTORE = "photo_comment_restore"

    AUDIO_NEW = "audio_new"

    VIDEO_NEW = "video_new"
    VIDEO_COMMENT_NEW = "video_comment_new"
    VIDEO_COMMENT_EDIT = "video_comment_edit"
    VIDEO_COMMENT_DELETE = "video_comment_delete"
    VIDEO_COMMENT_RESTORE = "video_comment_restore"

    WALL_POST_NEW = "wall_post_new"
    WALL_REPOST = "wall_repost"
    WALL_REPLY_NEW = "wall_reply_new"
    WALL_REPLY_EDIT = "wall_reply_edit"
    WALL_REPLY_DELETE = "wall_reply_delete"
    WALL_REPLY_RESTORE = "wall_reply_restore"

    BOARD_POST_NEW = "board_post_new"
    BOARD_POST_DELETE = "board_post_delete"
    BOARD_POST_RESTORE = "board_post_restore"

    MARKET_COMMENT_NEW = "market_comment_new"
    MARKET_COMMENT_EDIT = "market_comment_edit"
    MARKET_COMMENT_DELETE = "market_comment_delete"
    MARKET_COMMENT_RESTORE = "market_comment_restore"

    GROUP_LEAVE = "group_leave"
    GROUP_JOIN = "group_join"
    USER_BLOCK = "user_block"
    USER_UNBLOCK = "user_unblock"
    GROUP_CHANGE_SETTINGS = "group_change_settings"
    GROUP_CHANGE_PHOTO = "group_change_photo"
    GROUP_OFFICERS_EDIT = "group_officers_edit"

    POLL_VOTE_NEW = "poll_vote_new"


class DataProcessing:
    def __init__(self, event_poll, confirmation_key) -> None:
        super().__init__()
        self.event_poll = event_poll
        self.confirmation_key = confirmation_key

    def emit(self, data: dict):
        """
        Эммитим эвенты через дату

        :param data:
        :return:
        """

        # Объявим парочку переменных
        command, act_type, act_from, act_mid, act_text = None, None, None, None, None
        data_type = data.get("type")

        # Непосредственная обработка событий

        if DataTypes(data_type) == DataTypes.CONFIRMATION:
            return self.confirmation_key

        if DataTypes(data_type) == DataTypes.MESSAGE_NEW or DataTypes(data_type) == DataTypes.MESSAGE_REPLY:
            is_command = data.get("object").get("text").startswith("/")

            if is_command:
                command = data.get("object").get("text").split(" ")[0]

            if data.get("object").get("id") != 0:
                type = "private"
            else:
                type = "public"

            id = data.get("object").get("conversation_message_id")
            peer_id = data.get("object").get("peer_id")
            from_id = data.get("object").get("from_id")
            date = data.get("object").get("date")
            important = data.get("object").get("important")
            admin_author_id = data.get("object").get("admin_author_id")
            is_hidden = data.get("object").get("is_hidden")
            text = data.get("object").get("text")

            act_type, act_from, act_mid, act_text = None, None, None, None

            is_acted = data.get("object").get("action")
            if is_acted:
                act_type = data["object"]["action"]["type"]
                act_mid = data["object"]["action"].get("member_id")
                act_from = data["object"].get("from_id")
                act_text = data["object"]["action"].get("text")

            attachments = []

            if data.get("object").get("attachments"):
                for attach in data.get("object").get("attachments"):
                    a_type = attach["type"]
                    owner_id = attach[a_type].get("owner_id")
                    a_id = attach[a_type].get("id")

                    attachments.append("{}{}_{}".format(a_type, owner_id, a_id))

            message = Message(
                id=id,
                group_id=data.get("group_id"),
                is_out=data.get("object").get("out"),
                type=type,
                from_id=from_id,
                peer_id=peer_id,
                is_command=is_command,
                command=command,
                text=text,
                date=date,
                important=important,
                admin_author_id=admin_author_id,
                is_hidden=is_hidden,
                is_acted=is_acted,
                act=Act(act_type=act_type, act_text=act_text, act_mid=act_mid, act_from=act_from),
                attachments=Attachments(objects=attachments)
            )
            self.event_poll.emit(data_type, message, command=command)

            return "ok"

        if DataTypes(data_type) == DataTypes.MESSAGE_REPLY:
            return "ok"

        if DataTypes(data_type) == DataTypes.GROUP_JOIN:
            join = Join(
                group_id=data.get("group_id"),
                user_id=data.get("object").get("user_id"),
                join_type=data.get("object").get("join_type")
            )

            self.event_poll.emit("group_join", join)

            return "ok"

        if DataTypes(data_type) == DataTypes.GROUP_LEAVE:
            leave = Leave(
                group_id=data.get("group_id"),
                user_id=data.get("object").get("user_id"),
                self_leave=data.get("object").get("self")
            )

            self.event_poll.emit("group_leave", leave)

            return "ok"

        object = data.get("object") or {}
        object["type"] = data_type
        object["group_id"] = data.get("group_id")

        print(object)

        event = CallbackEvent(object)

        self.event_poll.emit(data_type, event)

        return "ok"
