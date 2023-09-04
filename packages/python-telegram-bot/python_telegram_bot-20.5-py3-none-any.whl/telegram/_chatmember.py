#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an object that represents a Telegram ChatMember."""
import datetime
from typing import TYPE_CHECKING, Dict, Final, Optional, Type

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ChatMember(TelegramObject):
    """Base class for Telegram ChatMember Objects.
    Currently, the following 6 types of chat members are supported:

    * :class:`telegram.ChatMemberOwner`
    * :class:`telegram.ChatMemberAdministrator`
    * :class:`telegram.ChatMemberMember`
    * :class:`telegram.ChatMemberRestricted`
    * :class:`telegram.ChatMemberLeft`
    * :class:`telegram.ChatMemberBanned`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user` and :attr:`status` are equal.

    Examples:
        :any:`Chat Member Bot <examples.chatmemberbot>`

    .. versionchanged:: 20.0

        * As of Bot API 5.3, :class:`ChatMember` is nothing but the base class for the subclasses
          listed above and is no longer returned directly by :meth:`~telegram.Bot.get_chat`.
          Therefore, most of the arguments and attributes were removed and you should no longer
          use :class:`ChatMember` directly.
        * The constant ``ChatMember.CREATOR`` was replaced by :attr:`~telegram.ChatMember.OWNER`
        * The constant ``ChatMember.KICKED`` was replaced by :attr:`~telegram.ChatMember.BANNED`

    Args:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat. Can be
            :attr:`~telegram.ChatMember.ADMINISTRATOR`, :attr:`~telegram.ChatMember.OWNER`,
            :attr:`~telegram.ChatMember.BANNED`, :attr:`~telegram.ChatMember.LEFT`,
            :attr:`~telegram.ChatMember.MEMBER` or :attr:`~telegram.ChatMember.RESTRICTED`.

    Attributes:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat. Can be
            :attr:`~telegram.ChatMember.ADMINISTRATOR`, :attr:`~telegram.ChatMember.OWNER`,
            :attr:`~telegram.ChatMember.BANNED`, :attr:`~telegram.ChatMember.LEFT`,
            :attr:`~telegram.ChatMember.MEMBER` or :attr:`~telegram.ChatMember.RESTRICTED`.

    """

    __slots__ = ("user", "status")

    ADMINISTRATOR: Final[str] = constants.ChatMemberStatus.ADMINISTRATOR
    """:const:`telegram.constants.ChatMemberStatus.ADMINISTRATOR`"""
    OWNER: Final[str] = constants.ChatMemberStatus.OWNER
    """:const:`telegram.constants.ChatMemberStatus.OWNER`"""
    BANNED: Final[str] = constants.ChatMemberStatus.BANNED
    """:const:`telegram.constants.ChatMemberStatus.BANNED`"""
    LEFT: Final[str] = constants.ChatMemberStatus.LEFT
    """:const:`telegram.constants.ChatMemberStatus.LEFT`"""
    MEMBER: Final[str] = constants.ChatMemberStatus.MEMBER
    """:const:`telegram.constants.ChatMemberStatus.MEMBER`"""
    RESTRICTED: Final[str] = constants.ChatMemberStatus.RESTRICTED
    """:const:`telegram.constants.ChatMemberStatus.RESTRICTED`"""

    def __init__(
        self,
        user: User,
        status: str,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required by all subclasses
        self.user: User = user
        self.status: str = status

        self._id_attrs = (self.user, self.status)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["ChatMember"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        _class_mapping: Dict[str, Type[ChatMember]] = {
            cls.OWNER: ChatMemberOwner,
            cls.ADMINISTRATOR: ChatMemberAdministrator,
            cls.MEMBER: ChatMemberMember,
            cls.RESTRICTED: ChatMemberRestricted,
            cls.LEFT: ChatMemberLeft,
            cls.BANNED: ChatMemberBanned,
        }

        if cls is ChatMember and data.get("status") in _class_mapping:
            return _class_mapping[data.pop("status")].de_json(data=data, bot=bot)

        data["user"] = User.de_json(data.get("user"), bot)
        if "until_date" in data:
            # Get the local timezone from the bot if it has defaults
            loc_tzinfo = extract_tzinfo_from_defaults(bot)

            data["until_date"] = from_timestamp(data["until_date"], tzinfo=loc_tzinfo)

        # This is a deprecated field that TG still returns for backwards compatibility
        # Let's filter it out to speed up the de-json process
        if cls is ChatMemberRestricted and data.get("can_send_media_messages") is not None:
            api_kwargs = {"can_send_media_messages": data.pop("can_send_media_messages")}
            return super()._de_json(data=data, bot=bot, api_kwargs=api_kwargs)

        return super().de_json(data=data, bot=bot)


class ChatMemberOwner(ChatMember):
    """
    Represents a chat member that owns the chat
    and has all administrator privileges.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the
            user's presence in the chat is hidden.
        custom_title (:obj:`str`, optional): Custom title for this user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.OWNER`.
        user (:class:`telegram.User`): Information about the user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the user's
            presence in the chat is hidden.
        custom_title (:obj:`str`): Optional. Custom title for
            this user.
    """

    __slots__ = ("is_anonymous", "custom_title")

    def __init__(
        self,
        user: User,
        is_anonymous: bool,
        custom_title: Optional[str] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(status=ChatMember.OWNER, user=user, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.is_anonymous: bool = is_anonymous
            self.custom_title: Optional[str] = custom_title


class ChatMemberAdministrator(ChatMember):
    """
    Represents a chat member that has some additional privileges.

    .. versionadded:: 13.7
    .. versionchanged:: 20.0

       * Argument and attribute ``can_manage_voice_chats`` were renamed to
         :paramref:`can_manage_video_chats` and  :attr:`can_manage_video_chats` in accordance to
         Bot API 6.0.
       * The argument :paramref:`can_manage_topics` was added, which changes the position of the
         optional argument :paramref:`custom_title`.

    Args:
        user (:class:`telegram.User`): Information about the user.
        can_be_edited (:obj:`bool`): :obj:`True`, if the bot
            is allowed to edit administrator privileges of that user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the  user's
            presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator
            can access the chat event log, chat statistics, message statistics in
            channels, see channel members, see anonymous administrators in supergroups
            and ignore slow mode. Implied by any other administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the
            administrator can delete messages of other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the
            administrator can manage video chats.

            .. versionadded:: 20.0
        can_restrict_members (:obj:`bool`): :obj:`True`, if the
            administrator can restrict, ban or unban chat members.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator
            can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by
            administrators that were appointed by the user).
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_post_messages (:obj:`bool`, optional): :obj:`True`, if the
            administrator can post in the channel, channels only.
        can_edit_messages (:obj:`bool`, optional): :obj:`True`, if the
            administrator can edit messages of other users and can pin
            messages; channels only.
        can_pin_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_manage_topics (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to create, rename, close, and reopen forum topics; supergroups only.

            .. versionadded:: 20.0
        custom_title (:obj:`str`, optional): Custom title for this user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.ADMINISTRATOR`.
        user (:class:`telegram.User`): Information about the user.
        can_be_edited (:obj:`bool`): :obj:`True`, if the bot
            is allowed to edit administrator privileges of that user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the  user's
            presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator
            can access the chat event log, chat statistics, message statistics in
            channels, see channel members, see anonymous administrators in supergroups
            and ignore slow mode. Implied by any other administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the
            administrator can delete messages of other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the
            administrator can manage video chats.

            .. versionadded:: 20.0
        can_restrict_members (:obj:`bool`): :obj:`True`, if the
            administrator can restrict, ban or unban chat members.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator can add new
            administrators with a subset of their own privileges or demote administrators
            that they have promoted, directly or indirectly (promoted by administrators that
            were appointed by the user).
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_post_messages (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can post in the channel, channels only.
        can_edit_messages (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can edit messages of other users and can pin
            messages; channels only.
        can_pin_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_manage_topics (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to create, rename, close, and reopen forum topics; supergroups only

            .. versionadded:: 20.0
        custom_title (:obj:`str`): Optional. Custom title for this user.
    """

    __slots__ = (
        "can_be_edited",
        "is_anonymous",
        "can_manage_chat",
        "can_delete_messages",
        "can_manage_video_chats",
        "can_restrict_members",
        "can_promote_members",
        "can_change_info",
        "can_invite_users",
        "can_post_messages",
        "can_edit_messages",
        "can_pin_messages",
        "can_manage_topics",
        "custom_title",
    )

    def __init__(
        self,
        user: User,
        can_be_edited: bool,
        is_anonymous: bool,
        can_manage_chat: bool,
        can_delete_messages: bool,
        can_manage_video_chats: bool,
        can_restrict_members: bool,
        can_promote_members: bool,
        can_change_info: bool,
        can_invite_users: bool,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,
        custom_title: Optional[str] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(status=ChatMember.ADMINISTRATOR, user=user, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.can_be_edited: bool = can_be_edited
            self.is_anonymous: bool = is_anonymous
            self.can_manage_chat: bool = can_manage_chat
            self.can_delete_messages: bool = can_delete_messages
            self.can_manage_video_chats: bool = can_manage_video_chats
            self.can_restrict_members: bool = can_restrict_members
            self.can_promote_members: bool = can_promote_members
            self.can_change_info: bool = can_change_info
            self.can_invite_users: bool = can_invite_users
            self.can_post_messages: Optional[bool] = can_post_messages
            self.can_edit_messages: Optional[bool] = can_edit_messages
            self.can_pin_messages: Optional[bool] = can_pin_messages
            self.can_manage_topics: Optional[bool] = can_manage_topics
            self.custom_title: Optional[str] = custom_title


class ChatMemberMember(ChatMember):
    """
    Represents a chat member that has no additional
    privileges or restrictions.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.MEMBER`.
        user (:class:`telegram.User`): Information about the user.

    """

    __slots__ = ()

    def __init__(
        self,
        user: User,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(status=ChatMember.MEMBER, user=user, api_kwargs=api_kwargs)
        self._freeze()


class ChatMemberRestricted(ChatMember):
    """
    Represents a chat member that is under certain restrictions
    in the chat. Supergroups only.

    .. versionadded:: 13.7
    .. versionchanged:: 20.0
       All arguments were made positional and their order was changed.
       The argument can_manage_topics was added.

    .. versionchanged:: 20.5
      Removed deprecated argument and attribute ``can_send_media_messages``.

    Args:
        user (:class:`telegram.User`): Information about the user.
        is_member (:obj:`bool`): :obj:`True`, if the user is a
            member of the chat at the moment of the request.
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_send_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send text messages, contacts, invoices, locations and venues.
        can_send_polls (:obj:`bool`): :obj:`True`, if the user is allowed
            to send polls.
        can_send_other_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send animations, games, stickers and use inline bots.
        can_add_web_page_previews (:obj:`bool`): :obj:`True`, if the user is
           allowed to add web page previews to their messages.
        can_manage_topics (:obj:`bool`): :obj:`True`, if the user is allowed to create
            forum topics.

            .. versionadded:: 20.0
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|
        can_send_audios (:obj:`bool`): :obj:`True`, if the user is allowed to send audios.

            .. versionadded:: 20.1
        can_send_documents (:obj:`bool`): :obj:`True`, if the user is allowed to send documents.

            .. versionadded:: 20.1
        can_send_photos (:obj:`bool`): :obj:`True`, if the user is allowed to send photos.

            .. versionadded:: 20.1
        can_send_videos (:obj:`bool`): :obj:`True`, if the user is allowed to send videos.

            .. versionadded:: 20.1
        can_send_video_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send video
            notes.

            .. versionadded:: 20.1
        can_send_voice_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send voice
            notes.

            .. versionadded:: 20.1

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.RESTRICTED`.
        user (:class:`telegram.User`): Information about the user.
        is_member (:obj:`bool`): :obj:`True`, if the user is a
            member of the chat at the moment of the request.
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_send_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send text messages, contacts, locations and venues.
        can_send_polls (:obj:`bool`): :obj:`True`, if the user is allowed
            to send polls.
        can_send_other_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send animations, games, stickers and use inline bots.
        can_add_web_page_previews (:obj:`bool`): :obj:`True`, if the user is
           allowed to add web page previews to their messages.
        can_manage_topics (:obj:`bool`): :obj:`True`, if the user is allowed to create
            forum topics.

            .. versionadded:: 20.0
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|
        can_send_audios (:obj:`bool`): :obj:`True`, if the user is allowed to send audios.

            .. versionadded:: 20.1
        can_send_documents (:obj:`bool`): :obj:`True`, if the user is allowed to send documents.

            .. versionadded:: 20.1
        can_send_photos (:obj:`bool`): :obj:`True`, if the user is allowed to send photos.

            .. versionadded:: 20.1
        can_send_videos (:obj:`bool`): :obj:`True`, if the user is allowed to send videos.

            .. versionadded:: 20.1
        can_send_video_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send video
            notes.

            .. versionadded:: 20.1
        can_send_voice_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send voice
            notes.

            .. versionadded:: 20.1

    """

    __slots__ = (
        "is_member",
        "can_change_info",
        "can_invite_users",
        "can_pin_messages",
        "can_send_messages",
        "can_send_polls",
        "can_send_other_messages",
        "can_add_web_page_previews",
        "can_manage_topics",
        "until_date",
        "can_send_audios",
        "can_send_documents",
        "can_send_photos",
        "can_send_videos",
        "can_send_video_notes",
        "can_send_voice_notes",
    )

    def __init__(
        self,
        user: User,
        is_member: bool,
        can_change_info: bool,
        can_invite_users: bool,
        can_pin_messages: bool,
        can_send_messages: bool,
        can_send_polls: bool,
        can_send_other_messages: bool,
        can_add_web_page_previews: bool,
        can_manage_topics: bool,
        until_date: datetime.datetime,
        can_send_audios: bool,
        can_send_documents: bool,
        can_send_photos: bool,
        can_send_videos: bool,
        can_send_video_notes: bool,
        can_send_voice_notes: bool,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(status=ChatMember.RESTRICTED, user=user, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.is_member: bool = is_member
            self.can_change_info: bool = can_change_info
            self.can_invite_users: bool = can_invite_users
            self.can_pin_messages: bool = can_pin_messages
            self.can_send_messages: bool = can_send_messages
            self.can_send_polls: bool = can_send_polls
            self.can_send_other_messages: bool = can_send_other_messages
            self.can_add_web_page_previews: bool = can_add_web_page_previews
            self.can_manage_topics: bool = can_manage_topics
            self.until_date: datetime.datetime = until_date
            self.can_send_audios: bool = can_send_audios
            self.can_send_documents: bool = can_send_documents
            self.can_send_photos: bool = can_send_photos
            self.can_send_videos: bool = can_send_videos
            self.can_send_video_notes: bool = can_send_video_notes
            self.can_send_voice_notes: bool = can_send_voice_notes


class ChatMemberLeft(ChatMember):
    """
    Represents a chat member that isn't currently a member of the chat,
    but may join it themselves.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.LEFT`.
        user (:class:`telegram.User`): Information about the user.
    """

    __slots__ = ()

    def __init__(
        self,
        user: User,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(status=ChatMember.LEFT, user=user, api_kwargs=api_kwargs)
        self._freeze()


class ChatMemberBanned(ChatMember):
    """
    Represents a chat member that was banned in the chat and
    can't return to the chat or view chat messages.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.BANNED`.
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|

    """

    __slots__ = ("until_date",)

    def __init__(
        self,
        user: User,
        until_date: datetime.datetime,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(status=ChatMember.BANNED, user=user, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.until_date: datetime.datetime = until_date
