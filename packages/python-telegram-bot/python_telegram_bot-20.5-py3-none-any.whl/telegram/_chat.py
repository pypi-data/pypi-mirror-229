#!/usr/bin/env python
# pylint: disable=redefined-builtin
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
"""This module contains an object that represents a Telegram Chat."""
from datetime import datetime
from html import escape
from typing import TYPE_CHECKING, Final, Optional, Sequence, Tuple, Union

from telegram import constants
from telegram._chatlocation import ChatLocation
from telegram._chatpermissions import ChatPermissions
from telegram._files.chatphoto import ChatPhoto
from telegram._forumtopic import ForumTopic
from telegram._menubutton import MenuButton
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import (
    CorrectOptionID,
    DVInput,
    FileInput,
    JSONDict,
    ODVInput,
    ReplyMarkup,
)
from telegram.helpers import escape_markdown
from telegram.helpers import mention_html as helpers_mention_html
from telegram.helpers import mention_markdown as helpers_mention_markdown

if TYPE_CHECKING:
    from telegram import (
        Animation,
        Audio,
        Bot,
        ChatInviteLink,
        ChatMember,
        Contact,
        Document,
        InlineKeyboardMarkup,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        LabeledPrice,
        Location,
        Message,
        MessageEntity,
        MessageId,
        PhotoSize,
        Sticker,
        Venue,
        Video,
        VideoNote,
        Voice,
    )


class Chat(TelegramObject):
    """This object represents a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    .. versionchanged:: 20.0

        * Removed the deprecated methods ``kick_member`` and ``get_members_count``.
        * The following are now keyword-only arguments in Bot methods:
          ``location``, ``filename``, ``contact``, ``{read, write, connect, pool}_timeout``,
          ``api_kwargs``. Use a named argument for those,
          and notice that some positional arguments changed position as a result.

    .. versionchanged:: 20.0
        Removed the attribute ``all_members_are_administrators``. As long as Telegram provides
        this field for backwards compatibility, it is available through
        :attr:`~telegram.TelegramObject.api_kwargs`.

    Args:
        id (:obj:`int`): Unique identifier for this chat. This number may be greater than 32 bits
            and some programming languages may have difficulty/silent defects in interpreting it.
            But it is smaller than 52 bits, so a signed 64-bit integer or double-precision float
            type are safe for storing this identifier.
        type (:obj:`str`): Type of chat, can be either :attr:`PRIVATE`, :attr:`GROUP`,
            :attr:`SUPERGROUP` or :attr:`CHANNEL`.
        title (:obj:`str`, optional): Title, for supergroups, channels and group chats.
        username (:obj:`str`, optional): Username, for private chats, supergroups and channels if
            available.
        first_name (:obj:`str`, optional): First name of the other party in a private chat.
        last_name (:obj:`str`, optional): Last name of the other party in a private chat.
        photo (:class:`telegram.ChatPhoto`, optional): Chat photo.
            Returned only in :meth:`telegram.Bot.get_chat`.
        bio (:obj:`str`, optional): Bio of the other party in a private chat. Returned only in
            :meth:`telegram.Bot.get_chat`.
        has_private_forwards (:obj:`bool`, optional): :obj:`True`, if privacy settings of the other
            party in the private chat allows to use ``tg://user?id=<user_id>`` links only in chats
            with the user. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.9
        description (:obj:`str`, optional): Description, for groups, supergroups and channel chats.
            Returned only in :meth:`telegram.Bot.get_chat`.
        invite_link (:obj:`str`, optional): Primary invite link, for groups, supergroups and
            channel. Returned only in :meth:`telegram.Bot.get_chat`.
        pinned_message (:class:`telegram.Message`, optional): The most recent pinned message
            (by sending date). Returned only in :meth:`telegram.Bot.get_chat`.
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups. Returned only in :meth:`telegram.Bot.get_chat`.
        slow_mode_delay (:obj:`int`, optional): For supergroups, the minimum allowed delay between
            consecutive messages sent by each unprivileged user.
            Returned only in :meth:`telegram.Bot.get_chat`.
        message_auto_delete_time (:obj:`int`, optional): The time after which all messages sent to
            the chat will be automatically deleted; in seconds. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.4
        has_protected_content (:obj:`bool`, optional): :obj:`True`, if messages from the chat can't
            be forwarded to other chats. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.9

        sticker_set_name (:obj:`str`, optional): For supergroups, name of group sticker set.
            Returned only in :meth:`telegram.Bot.get_chat`.
        can_set_sticker_set (:obj:`bool`, optional): :obj:`True`, if the bot can change group the
            sticker set. Returned only in :meth:`telegram.Bot.get_chat`.
        linked_chat_id (:obj:`int`, optional): Unique identifier for the linked chat, i.e. the
            discussion group identifier for a channel and vice versa; for supergroups and channel
            chats. Returned only in :meth:`telegram.Bot.get_chat`.
        location (:class:`telegram.ChatLocation`, optional): For supergroups, the location to which
            the supergroup is connected. Returned only in :meth:`telegram.Bot.get_chat`.
        join_to_send_messages (:obj:`bool`, optional): :obj:`True`, if users need to join the
            supergroup before they can send messages. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        join_by_request (:obj:`bool`, optional): :obj:`True`, if all users directly joining the
            supergroup need to be approved by supergroup administrators. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        has_restricted_voice_and_video_messages (:obj:`bool`, optional): :obj:`True`, if the
            privacy settings of the other party restrict sending voice and video note messages
            in the private chat. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        is_forum (:obj:`bool`, optional): :obj:`True`, if the supergroup chat is a forum
            (has topics_ enabled).

            .. versionadded:: 20.0
        active_usernames (Sequence[:obj:`str`], optional):  If set, the list of all `active chat
            usernames <https://telegram.org/blog/topics-in-groups-collectible-usernames\
            #collectible-usernames>`_; for private chats, supergroups and channels. Returned
            only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        emoji_status_custom_emoji_id (:obj:`str`, optional): Custom emoji identifier of emoji
            status of the other party in a private chat. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        emoji_status_expiration_date (:class:`datetime.datetime`, optional): Expiration date of
            emoji status of the other party in a private chat, in seconds. Returned only in
            :meth:`telegram.Bot.get_chat`.
            |datetime_localization|

            .. versionadded:: 20.5
        has_aggressive_anti_spam_enabled (:obj:`bool`, optional): :obj:`True`, if aggressive
            anti-spam checks are enabled in the supergroup. The field is only available to chat
            administrators. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        has_hidden_members (:obj:`bool`, optional): :obj:`True`, if non-administrators can only
            get the list of bots and administrators in the chat. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0

    Attributes:
        id (:obj:`int`): Unique identifier for this chat. This number may be greater than 32 bits
            and some programming languages may have difficulty/silent defects in interpreting it.
            But it is smaller than 52 bits, so a signed 64-bit integer or double-precision float
            type are safe for storing this identifier.
        type (:obj:`str`): Type of chat, can be either :attr:`PRIVATE`, :attr:`GROUP`,
            :attr:`SUPERGROUP` or :attr:`CHANNEL`.
        title (:obj:`str`): Optional. Title, for supergroups, channels and group chats.
        username (:obj:`str`): Optional. Username, for private chats, supergroups and channels if
            available.
        first_name (:obj:`str`): Optional. First name of the other party in a private chat.
        last_name (:obj:`str`): Optional. Last name of the other party in a private chat.
        photo (:class:`telegram.ChatPhoto`): Optional. Chat photo.
            Returned only in :meth:`telegram.Bot.get_chat`.
        bio (:obj:`str`): Optional. Bio of the other party in a private chat. Returned only in
            :meth:`telegram.Bot.get_chat`.
        has_private_forwards (:obj:`bool`): Optional. :obj:`True`, if privacy settings of the other
            party in the private chat allows to use ``tg://user?id=<user_id>`` links only in chats
            with the user. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.9
        description (:obj:`str`): Optional. Description, for groups, supergroups and channel chats.
            Returned only in :meth:`telegram.Bot.get_chat`.
        invite_link (:obj:`str`): Optional. Primary invite link, for groups, supergroups and
            channel. Returned only in :meth:`telegram.Bot.get_chat`.
        pinned_message (:class:`telegram.Message`): Optional. The most recent pinned message
            (by sending date). Returned only in :meth:`telegram.Bot.get_chat`.
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups. Returned only in :meth:`telegram.Bot.get_chat`.
        slow_mode_delay (:obj:`int`): Optional. For supergroups, the minimum allowed delay between
            consecutive messages sent by each unprivileged user. Returned only in
            :meth:`telegram.Bot.get_chat`.
        message_auto_delete_time (:obj:`int`): Optional. The time after which all messages sent to
            the chat will be automatically deleted; in seconds. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.4
        has_protected_content (:obj:`bool`): Optional. :obj:`True`, if messages from the chat can't
            be forwarded to other chats. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.9
        sticker_set_name (:obj:`str`): Optional. For supergroups, name of Group sticker set.
            Returned only in :meth:`telegram.Bot.get_chat`.
        can_set_sticker_set (:obj:`bool`): Optional. :obj:`True`, if the bot can change group the
            sticker set. Returned only in :meth:`telegram.Bot.get_chat`.
        linked_chat_id (:obj:`int`): Optional. Unique identifier for the linked chat, i.e. the
            discussion group identifier for a channel and vice versa; for supergroups and channel
            chats. Returned only in :meth:`telegram.Bot.get_chat`.
        location (:class:`telegram.ChatLocation`): Optional. For supergroups, the location to which
            the supergroup is connected. Returned only in :meth:`telegram.Bot.get_chat`.
        join_to_send_messages (:obj:`bool`): Optional. :obj:`True`, if users need to join
            the supergroup before they can send messages. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        join_by_request (:obj:`bool`): Optional. :obj:`True`, if all users directly
            joining the supergroup need to be approved by supergroup administrators. Returned only
            in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        has_restricted_voice_and_video_messages (:obj:`bool`): Optional. :obj:`True`, if the
            privacy settings of the other party restrict sending voice and video note messages
            in the private chat. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        is_forum (:obj:`bool`): Optional. :obj:`True`, if the supergroup chat is a forum
            (has topics_ enabled).

            .. versionadded:: 20.0
        active_usernames (Tuple[:obj:`str`]): Optional. If set, the list of all `active chat
            usernames <https://telegram.org/blog/topics-in-groups-collectible-usernames\
            #collectible-usernames>`_; for private chats, supergroups and channels. Returned
            only in :meth:`telegram.Bot.get_chat`.
            This list is empty if the chat has no active usernames or this chat instance was not
            obtained via :meth:`~telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        emoji_status_custom_emoji_id (:obj:`str`): Optional. Custom emoji identifier of emoji
            status of the other party in a private chat. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        emoji_status_expiration_date (:class:`datetime.datetime`, optional): Expiration date of
            emoji status of the other party in a private chat, in seconds. Returned only in
            :meth:`telegram.Bot.get_chat`.
            |datetime_localization|

            .. versionadded:: 20.5
        has_aggressive_anti_spam_enabled (:obj:`bool`): Optional. :obj:`True`, if aggressive
            anti-spam checks are enabled in the supergroup. The field is only available to chat
            administrators. Returned only in :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        has_hidden_members (:obj:`bool`): Optional. :obj:`True`, if non-administrators can only
            get the list of bots and administrators in the chat. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 20.0

    .. _topics: https://telegram.org/blog/topics-in-groups-collectible-usernames#topics-in-groups
    """

    __slots__ = (
        "bio",
        "id",
        "type",
        "last_name",
        "sticker_set_name",
        "slow_mode_delay",
        "location",
        "first_name",
        "permissions",
        "invite_link",
        "pinned_message",
        "description",
        "can_set_sticker_set",
        "username",
        "title",
        "photo",
        "linked_chat_id",
        "message_auto_delete_time",
        "has_protected_content",
        "has_private_forwards",
        "join_to_send_messages",
        "join_by_request",
        "has_restricted_voice_and_video_messages",
        "is_forum",
        "active_usernames",
        "emoji_status_custom_emoji_id",
        "emoji_status_expiration_date",
        "has_hidden_members",
        "has_aggressive_anti_spam_enabled",
    )

    SENDER: Final[str] = constants.ChatType.SENDER
    """:const:`telegram.constants.ChatType.SENDER`

    .. versionadded:: 13.5
    """
    PRIVATE: Final[str] = constants.ChatType.PRIVATE
    """:const:`telegram.constants.ChatType.PRIVATE`"""
    GROUP: Final[str] = constants.ChatType.GROUP
    """:const:`telegram.constants.ChatType.GROUP`"""
    SUPERGROUP: Final[str] = constants.ChatType.SUPERGROUP
    """:const:`telegram.constants.ChatType.SUPERGROUP`"""
    CHANNEL: Final[str] = constants.ChatType.CHANNEL
    """:const:`telegram.constants.ChatType.CHANNEL`"""

    def __init__(
        self,
        id: int,
        type: str,
        title: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        photo: Optional[ChatPhoto] = None,
        description: Optional[str] = None,
        invite_link: Optional[str] = None,
        pinned_message: Optional["Message"] = None,
        permissions: Optional[ChatPermissions] = None,
        sticker_set_name: Optional[str] = None,
        can_set_sticker_set: Optional[bool] = None,
        slow_mode_delay: Optional[int] = None,
        bio: Optional[str] = None,
        linked_chat_id: Optional[int] = None,
        location: Optional[ChatLocation] = None,
        message_auto_delete_time: Optional[int] = None,
        has_private_forwards: Optional[bool] = None,
        has_protected_content: Optional[bool] = None,
        join_to_send_messages: Optional[bool] = None,
        join_by_request: Optional[bool] = None,
        has_restricted_voice_and_video_messages: Optional[bool] = None,
        is_forum: Optional[bool] = None,
        active_usernames: Optional[Sequence[str]] = None,
        emoji_status_custom_emoji_id: Optional[str] = None,
        emoji_status_expiration_date: Optional[datetime] = None,
        has_aggressive_anti_spam_enabled: Optional[bool] = None,
        has_hidden_members: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.id: int = id  # pylint: disable=invalid-name
        self.type: str = enum.get_member(constants.ChatType, type, type)
        # Optionals
        self.title: Optional[str] = title
        self.username: Optional[str] = username
        self.first_name: Optional[str] = first_name
        self.last_name: Optional[str] = last_name
        self.photo: Optional[ChatPhoto] = photo
        self.bio: Optional[str] = bio
        self.has_private_forwards: Optional[bool] = has_private_forwards
        self.description: Optional[str] = description
        self.invite_link: Optional[str] = invite_link
        self.pinned_message: Optional[Message] = pinned_message
        self.permissions: Optional[ChatPermissions] = permissions
        self.slow_mode_delay: Optional[int] = slow_mode_delay
        self.message_auto_delete_time: Optional[int] = (
            int(message_auto_delete_time) if message_auto_delete_time is not None else None
        )
        self.has_protected_content: Optional[bool] = has_protected_content
        self.sticker_set_name: Optional[str] = sticker_set_name
        self.can_set_sticker_set: Optional[bool] = can_set_sticker_set
        self.linked_chat_id: Optional[int] = linked_chat_id
        self.location: Optional[ChatLocation] = location
        self.join_to_send_messages: Optional[bool] = join_to_send_messages
        self.join_by_request: Optional[bool] = join_by_request
        self.has_restricted_voice_and_video_messages: Optional[
            bool
        ] = has_restricted_voice_and_video_messages
        self.is_forum: Optional[bool] = is_forum
        self.active_usernames: Tuple[str, ...] = parse_sequence_arg(active_usernames)
        self.emoji_status_custom_emoji_id: Optional[str] = emoji_status_custom_emoji_id
        self.emoji_status_expiration_date: Optional[datetime] = emoji_status_expiration_date
        self.has_aggressive_anti_spam_enabled: Optional[bool] = has_aggressive_anti_spam_enabled
        self.has_hidden_members: Optional[bool] = has_hidden_members

        self._id_attrs = (self.id,)

        self._freeze()

    @property
    def effective_name(self) -> Optional[str]:
        """
        :obj:`str`: Convenience property. Gives :attr:`title` if not :obj:`None`,
        else :attr:`full_name` if not :obj:`None`.

        .. versionadded:: 20.1
        """
        if self.title is not None:
            return self.title
        if self.full_name is not None:
            return self.full_name
        return None

    @property
    def full_name(self) -> Optional[str]:
        """
        :obj:`str`: Convenience property. If :attr:`first_name` is not :obj:`None`, gives
        :attr:`first_name` followed by (if available) :attr:`last_name`.

        Note:
            :attr:`full_name` will always be :obj:`None`, if the chat is a (super)group or
            channel.

        .. versionadded:: 13.2
        """
        if not self.first_name:
            return None
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If the chat has a :attr:`username`, returns a t.me
        link of the chat.
        """
        if self.username:
            return f"https://t.me/{self.username}"
        return None

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["Chat"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        data["emoji_status_expiration_date"] = from_timestamp(
            data.get("emoji_status_expiration_date"), tzinfo=loc_tzinfo
        )

        data["photo"] = ChatPhoto.de_json(data.get("photo"), bot)
        from telegram import Message  # pylint: disable=import-outside-toplevel

        data["pinned_message"] = Message.de_json(data.get("pinned_message"), bot)
        data["permissions"] = ChatPermissions.de_json(data.get("permissions"), bot)
        data["location"] = ChatLocation.de_json(data.get("location"), bot)

        api_kwargs = {}
        # This is a deprecated field that TG still returns for backwards compatibility
        # Let's filter it out to speed up the de-json process
        if "all_members_are_administrators" in data:
            api_kwargs["all_members_are_administrators"] = data.pop(
                "all_members_are_administrators"
            )

        return super()._de_json(data=data, bot=bot, api_kwargs=api_kwargs)

    def mention_markdown(self, name: Optional[str] = None) -> str:
        """
        Note:
            :tg-const:`telegram.constants.ParseMode.MARKDOWN` is a legacy mode, retained by
            Telegram for backward compatibility. You should use :meth:`mention_markdown_v2`
            instead.

        .. versionadded:: 20.0

        Args:
            name (:obj:`str`): The name used as a link for the chat. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the chat as markdown (version 1).

        Raises:
            :exc:`TypeError`: If the chat is a private chat and neither the :paramref:`name`
                nor the :attr:`first_name` is set, then throw an :exc:`TypeError`.
                If the chat is a public chat and neither the :paramref:`name` nor the :attr:`title`
                is set, then throw an :exc:`TypeError`. If chat is a private group chat, then
                throw an :exc:`TypeError`.

        """
        if self.type == self.PRIVATE:
            if name:
                return helpers_mention_markdown(self.id, name)
            if self.full_name:
                return helpers_mention_markdown(self.id, self.full_name)
            raise TypeError("Can not create a mention to a private chat without first name")
        if self.username:
            if name:
                return f"[{name}]({self.link})"
            if self.title:
                return f"[{self.title}]({self.link})"
            raise TypeError("Can not create a mention to a public chat without title")
        raise TypeError("Can not create a mention to a private group chat")

    def mention_markdown_v2(self, name: Optional[str] = None) -> str:
        """
        .. versionadded:: 20.0

        Args:
            name (:obj:`str`): The name used as a link for the chat. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the chat as markdown (version 2).

        Raises:
            :exc:`TypeError`: If the chat is a private chat and neither the :paramref:`name`
                nor the :attr:`first_name` is set, then throw an :exc:`TypeError`.
                If the chat is a public chat and neither the :paramref:`name` nor the :attr:`title`
                is set, then throw an :exc:`TypeError`. If chat is a private group chat, then
                throw an :exc:`TypeError`.

        """
        if self.type == self.PRIVATE:
            if name:
                return helpers_mention_markdown(self.id, name, version=2)
            if self.full_name:
                return helpers_mention_markdown(self.id, self.full_name, version=2)
            raise TypeError("Can not create a mention to a private chat without first name")
        if self.username:
            if name:
                return f"[{escape_markdown(name, version=2)}]({self.link})"
            if self.title:
                return f"[{escape_markdown(self.title, version=2)}]({self.link})"
            raise TypeError("Can not create a mention to a public chat without title")
        raise TypeError("Can not create a mention to a private group chat")

    def mention_html(self, name: Optional[str] = None) -> str:
        """
        .. versionadded:: 20.0

        Args:
            name (:obj:`str`): The name used as a link for the chat. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the chat as HTML.

        Raises:
            :exc:`TypeError`: If the chat is a private chat and neither the :paramref:`name`
                nor the :attr:`first_name` is set, then throw an :exc:`TypeError`.
                If the chat is a public chat and neither the :paramref:`name` nor the :attr:`title`
                is set, then throw an :exc:`TypeError`. If chat is a private group chat, then
                throw an :exc:`TypeError`.

        """
        if self.type == self.PRIVATE:
            if name:
                return helpers_mention_html(self.id, name)
            if self.full_name:
                return helpers_mention_html(self.id, self.full_name)
            raise TypeError("Can not create a mention to a private chat without first name")
        if self.username:
            if name:
                return f'<a href="{self.link}">{escape(name)}</a>'
            if self.title:
                return f'<a href="{self.link}">{escape(self.title)}</a>'
            raise TypeError("Can not create a mention to a public chat without title")
        raise TypeError("Can not create a mention to a private group chat")

    async def leave(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.leave_chat(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.leave_chat`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().leave_chat(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_administrators(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple["ChatMember", ...]:
        """Shortcut for::

             await bot.get_chat_administrators(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_chat_administrators`.

        Returns:
            Tuple[:class:`telegram.ChatMember`]: A tuple of administrators in a chat. An Array of
            :class:`telegram.ChatMember` objects that contains information about all
            chat administrators except other bots. If the chat is a group or a supergroup
            and no administrators were appointed, only the creator will be returned.

        """
        return await self.get_bot().get_chat_administrators(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_member_count(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> int:
        """Shortcut for::

             await bot.get_chat_member_count(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_chat_member_count`.

        Returns:
            :obj:`int`
        """
        return await self.get_bot().get_chat_member_count(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_member(
        self,
        user_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "ChatMember":
        """Shortcut for::

             await bot.get_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.get_chat_member`.

        Returns:
            :class:`telegram.ChatMember`

        """
        return await self.get_bot().get_chat_member(
            chat_id=self.id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def ban_member(
        self,
        user_id: Union[str, int],
        revoke_messages: Optional[bool] = None,
        until_date: Optional[Union[int, datetime]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.ban_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.ban_chat_member`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().ban_chat_member(
            chat_id=self.id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            until_date=until_date,
            api_kwargs=api_kwargs,
            revoke_messages=revoke_messages,
        )

    async def ban_sender_chat(
        self,
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.ban_chat_sender_chat(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.ban_chat_sender_chat`.

        .. versionadded:: 13.9

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().ban_chat_sender_chat(
            chat_id=self.id,
            sender_chat_id=sender_chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def ban_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.ban_chat_sender_chat(
                 sender_chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.ban_chat_sender_chat`.

        .. versionadded:: 13.9

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().ban_chat_sender_chat(
            chat_id=chat_id,
            sender_chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unban_sender_chat(
        self,
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.unban_chat_sender_chat(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unban_chat_sender_chat`.

        .. versionadded:: 13.9

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unban_chat_sender_chat(
            chat_id=self.id,
            sender_chat_id=sender_chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unban_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.unban_chat_sender_chat(
                 sender_chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unban_chat_sender_chat`.

        .. versionadded:: 13.9

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unban_chat_sender_chat(
            chat_id=chat_id,
            sender_chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unban_member(
        self,
        user_id: Union[str, int],
        only_if_banned: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.unban_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.unban_chat_member`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unban_chat_member(
            chat_id=self.id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            only_if_banned=only_if_banned,
        )

    async def promote_member(
        self,
        user_id: Union[str, int],
        can_change_info: Optional[bool] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_promote_members: Optional[bool] = None,
        is_anonymous: Optional[bool] = None,
        can_manage_chat: Optional[bool] = None,
        can_manage_video_chats: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.promote_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.promote_chat_member`.

        .. versionadded:: 13.2
        .. versionchanged:: 20.0
           The argument ``can_manage_voice_chats`` was renamed to
           :paramref:`~telegram.Bot.promote_chat_member.can_manage_video_chats` in accordance to
           Bot API 6.0.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().promote_chat_member(
            chat_id=self.id,
            user_id=user_id,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_pin_messages=can_pin_messages,
            can_promote_members=can_promote_members,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            is_anonymous=is_anonymous,
            can_manage_chat=can_manage_chat,
            can_manage_video_chats=can_manage_video_chats,
            can_manage_topics=can_manage_topics,
        )

    async def restrict_member(
        self,
        user_id: Union[str, int],
        permissions: ChatPermissions,
        until_date: Optional[Union[int, datetime]] = None,
        use_independent_chat_permissions: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.restrict_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.restrict_chat_member`.

        .. versionadded:: 13.2

        .. versionadded:: 20.1
            Added :paramref:`~telegram.Bot.restrict_chat_member.use_independent_chat_permissions`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().restrict_chat_member(
            chat_id=self.id,
            user_id=user_id,
            permissions=permissions,
            until_date=until_date,
            use_independent_chat_permissions=use_independent_chat_permissions,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_permissions(
        self,
        permissions: ChatPermissions,
        use_independent_chat_permissions: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.set_chat_permissions(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_permissions`.

        .. versionadded:: 20.1
            Added :paramref:`~telegram.Bot.set_chat_permissions.use_independent_chat_permissions`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().set_chat_permissions(
            chat_id=self.id,
            permissions=permissions,
            use_independent_chat_permissions=use_independent_chat_permissions,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_administrator_custom_title(
        self,
        user_id: Union[int, str],
        custom_title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.set_chat_administrator_custom_title(
                 update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_administrator_custom_title`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().set_chat_administrator_custom_title(
            chat_id=self.id,
            user_id=user_id,
            custom_title=custom_title,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_photo(
        self,
        photo: FileInput,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.set_chat_photo(
                 chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_photo`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().set_chat_photo(
            chat_id=self.id,
            photo=photo,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def delete_photo(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.delete_chat_photo(
                 chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.delete_chat_photo`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().delete_chat_photo(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_title(
        self,
        title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.set_chat_title(
                 chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_title`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().set_chat_title(
            chat_id=self.id,
            title=title,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_description(
        self,
        description: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.set_chat_description(
                 chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_description`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().set_chat_description(
            chat_id=self.id,
            description=description,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def pin_message(
        self,
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

              await bot.pin_chat_message(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.pin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().pin_chat_message(
            chat_id=self.id,
            message_id=message_id,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unpin_message(
        self,
        message_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

              await bot.unpin_chat_message(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unpin_chat_message(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            message_id=message_id,
        )

    async def unpin_all_messages(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

              await bot.unpin_all_chat_messages(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_all_chat_messages`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unpin_all_chat_messages(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def send_message(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_message(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_message(
            chat_id=self.id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def send_media_group(
        self,
        media: Sequence[
            Union["InputMediaAudio", "InputMediaDocument", "InputMediaPhoto", "InputMediaVideo"]
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
    ) -> Tuple["Message", ...]:
        """Shortcut for::

             await bot.send_media_group(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_media_group`.

        Returns:
            Tuple[:class:`telegram.Message`]: On success, a tuple of :class:`~telegram.Message`
            instances that were sent is returned.

        """
        return await self.get_bot().send_media_group(
            chat_id=self.id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )

    async def send_chat_action(
        self,
        action: str,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.send_chat_action(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_chat_action`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().send_chat_action(
            chat_id=self.id,
            action=action,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    send_action = send_chat_action
    """Alias for :attr:`send_chat_action`"""

    async def send_photo(
        self,
        photo: Union[FileInput, "PhotoSize"],
        caption: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        *,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_photo(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_photo`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_photo(
            chat_id=self.id,
            photo=photo,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            has_spoiler=has_spoiler,
        )

    async def send_contact(
        self,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        vcard: Optional[str] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        contact: Optional["Contact"] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_contact(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_contact`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_contact(
            chat_id=self.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            contact=contact,
            vcard=vcard,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_audio(
        self,
        audio: Union[FileInput, "Audio"],
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        *,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_audio(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_audio`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_audio(
            chat_id=self.id,
            audio=audio,
            duration=duration,
            performer=performer,
            title=title,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            thumbnail=thumbnail,
        )

    async def send_document(
        self,
        document: Union[FileInput, "Document"],
        caption: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_content_type_detection: Optional[bool] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        *,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_document(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_document`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_document(
            chat_id=self.id,
            document=document,
            filename=filename,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            thumbnail=thumbnail,
            api_kwargs=api_kwargs,
            disable_content_type_detection=disable_content_type_detection,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_dice(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        emoji: Optional[str] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_dice(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_dice`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_dice(
            chat_id=self.id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            emoji=emoji,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_game(
        self,
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_game(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_game`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_game(
            chat_id=self.id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: Sequence["LabeledPrice"],
        start_parameter: Optional[str] = None,
        photo_url: Optional[str] = None,
        photo_size: Optional[int] = None,
        photo_width: Optional[int] = None,
        photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        provider_data: Optional[Union[str, object]] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[Sequence[int]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_invoice(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_invoice`.

        Warning:
            As of API 5.2 :paramref:`start_parameter <telegram.Bot.send_invoice.start_parameter>`
            is an optional argument and therefore the
            order of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter
            :paramref:`start_parameter <telegram.Bot.send_invoice.start_parameter>` is optional.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_invoice(
            chat_id=self.id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            start_parameter=start_parameter,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            provider_data=provider_data,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_location(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        live_period: Optional[int] = None,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        location: Optional["Location"] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_location(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_location`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_location(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            location=location,
            live_period=live_period,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_animation(
        self,
        animation: Union[FileInput, "Animation"],
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        *,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_animation(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_animation`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_animation(
            chat_id=self.id,
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
            thumbnail=thumbnail,
        )

    async def send_sticker(
        self,
        sticker: Union[FileInput, "Sticker"],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        emoji: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_sticker(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_sticker`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_sticker(
            chat_id=self.id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            emoji=emoji,
        )

    async def send_venue(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        title: Optional[str] = None,
        address: Optional[str] = None,
        foursquare_id: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        foursquare_type: Optional[str] = None,
        google_place_id: Optional[str] = None,
        google_place_type: Optional[str] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        venue: Optional["Venue"] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_venue(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_venue`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_venue(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            venue=venue,
            foursquare_type=foursquare_type,
            api_kwargs=api_kwargs,
            google_place_id=google_place_id,
            google_place_type=google_place_type,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_video(
        self,
        video: Union[FileInput, "Video"],
        duration: Optional[int] = None,
        caption: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: Optional[bool] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        *,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_video(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_video(
            chat_id=self.id,
            video=video,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            width=width,
            height=height,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            thumbnail=thumbnail,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
        )

    async def send_video_note(
        self,
        video_note: Union[FileInput, "VideoNote"],
        duration: Optional[int] = None,
        length: Optional[int] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        *,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_video_note(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video_note`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_video_note(
            chat_id=self.id,
            video_note=video_note,
            duration=duration,
            length=length,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            thumbnail=thumbnail,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_voice(
        self,
        voice: Union[FileInput, "Voice"],
        duration: Optional[int] = None,
        caption: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_voice(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_voice`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_voice(
            chat_id=self.id,
            voice=voice,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_poll(
        self,
        question: str,
        options: Sequence[str],
        is_anonymous: Optional[bool] = None,
        type: Optional[str] = None,
        allows_multiple_answers: Optional[bool] = None,
        correct_option_id: Optional[CorrectOptionID] = None,
        is_closed: Optional[bool] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        explanation: Optional[str] = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: Optional[int] = None,
        close_date: Optional[Union[int, datetime]] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        explanation_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_poll(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_poll`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_poll(
            chat_id=self.id,
            question=question,
            options=options,
            is_anonymous=is_anonymous,
            type=type,  # pylint=pylint,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            is_closed=is_closed,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period,
            close_date=close_date,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            explanation_entities=explanation_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def send_copy(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "MessageId":
        """Shortcut for::

             await bot.copy_message(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().copy_message(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def copy_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "MessageId":
        """Shortcut for::

             await bot.copy_message(from_chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().copy_message(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def forward_from(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.forward_message(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_message`.

        .. seealso:: :meth:`forward_to`

        .. versionadded:: 20.0

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().forward_message(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def forward_to(
        self,
        chat_id: Union[int, str],
        message_id: int,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.forward_message(from_chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_message`.

        .. seealso:: :meth:`forward_from`

        .. versionadded:: 20.0

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().forward_message(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def export_invite_link(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> str:
        """Shortcut for::

             await bot.export_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.export_chat_invite_link`.

        .. versionadded:: 13.4

        Returns:
            :obj:`str`: New invite link on success.

        """
        return await self.get_bot().export_chat_invite_link(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def create_invite_link(
        self,
        expire_date: Optional[Union[int, datetime]] = None,
        member_limit: Optional[int] = None,
        name: Optional[str] = None,
        creates_join_request: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "ChatInviteLink":
        """Shortcut for::

             await bot.create_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.create_chat_invite_link`.

        .. versionadded:: 13.4

        .. versionchanged:: 13.8
           Edited signature according to the changes of
           :meth:`telegram.Bot.create_chat_invite_link`.

        Returns:
            :class:`telegram.ChatInviteLink`

        """
        return await self.get_bot().create_chat_invite_link(
            chat_id=self.id,
            expire_date=expire_date,
            member_limit=member_limit,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            name=name,
            creates_join_request=creates_join_request,
        )

    async def edit_invite_link(
        self,
        invite_link: Union[str, "ChatInviteLink"],
        expire_date: Optional[Union[int, datetime]] = None,
        member_limit: Optional[int] = None,
        name: Optional[str] = None,
        creates_join_request: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "ChatInviteLink":
        """Shortcut for::

             await bot.edit_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_chat_invite_link`.

        .. versionadded:: 13.4

        .. versionchanged:: 13.8
           Edited signature according to the changes of :meth:`telegram.Bot.edit_chat_invite_link`.

        Returns:
            :class:`telegram.ChatInviteLink`

        """
        return await self.get_bot().edit_chat_invite_link(
            chat_id=self.id,
            invite_link=invite_link,
            expire_date=expire_date,
            member_limit=member_limit,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            name=name,
            creates_join_request=creates_join_request,
        )

    async def revoke_invite_link(
        self,
        invite_link: Union[str, "ChatInviteLink"],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "ChatInviteLink":
        """Shortcut for::

             await bot.revoke_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.revoke_chat_invite_link`.

        .. versionadded:: 13.4

        Returns:
            :class:`telegram.ChatInviteLink`

        """
        return await self.get_bot().revoke_chat_invite_link(
            chat_id=self.id,
            invite_link=invite_link,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def approve_join_request(
        self,
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.approve_chat_join_request(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.approve_chat_join_request`.

        .. versionadded:: 13.8

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().approve_chat_join_request(
            chat_id=self.id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def decline_join_request(
        self,
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.decline_chat_join_request(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.decline_chat_join_request`.

        .. versionadded:: 13.8

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().decline_chat_join_request(
            chat_id=self.id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_menu_button(
        self,
        menu_button: Optional[MenuButton] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.set_chat_menu_button(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_menu_button`.

        Caution:
            Can only work, if the chat is a private chat.

        .. seealso:: :meth:`get_menu_button`

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().set_chat_menu_button(
            chat_id=self.id,
            menu_button=menu_button,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def create_forum_topic(
        self,
        name: str,
        icon_color: Optional[int] = None,
        icon_custom_emoji_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> ForumTopic:
        """Shortcut for::

             await bot.create_forum_topic(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.create_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :class:`telegram.ForumTopic`
        """
        return await self.get_bot().create_forum_topic(
            chat_id=self.id,
            name=name,
            icon_color=icon_color,
            icon_custom_emoji_id=icon_custom_emoji_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def edit_forum_topic(
        self,
        message_thread_id: int,
        name: Optional[str] = None,
        icon_custom_emoji_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.edit_forum_topic(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().edit_forum_topic(
            chat_id=self.id,
            message_thread_id=message_thread_id,
            name=name,
            icon_custom_emoji_id=icon_custom_emoji_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def close_forum_topic(
        self,
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.close_forum_topic(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.close_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().close_forum_topic(
            chat_id=self.id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reopen_forum_topic(
        self,
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.reopen_forum_topic(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.reopen_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().reopen_forum_topic(
            chat_id=self.id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def delete_forum_topic(
        self,
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.delete_forum_topic(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.delete_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().delete_forum_topic(
            chat_id=self.id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unpin_all_forum_topic_messages(
        self,
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.unpin_all_forum_topic_messages(chat_id=update.effective_chat.id,
                *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_all_forum_topic_messages`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().unpin_all_forum_topic_messages(
            chat_id=self.id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unpin_all_general_forum_topic_messages(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.unpin_all_general_forum_topic_messages(chat_id=update.effective_chat.id,
                *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_all_general_forum_topic_messages`.

        .. versionadded:: 20.5

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().unpin_all_general_forum_topic_messages(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def edit_general_forum_topic(
        self,
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.edit_general_forum_topic(
                chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_general_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().edit_general_forum_topic(
            chat_id=self.id,
            name=name,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def close_general_forum_topic(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.close_general_forum_topic(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.close_general_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().close_general_forum_topic(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reopen_general_forum_topic(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.reopen_general_forum_topic(
                chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.reopen_general_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().reopen_general_forum_topic(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def hide_general_forum_topic(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.hide_general_forum_topic(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.hide_general_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().hide_general_forum_topic(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unhide_general_forum_topic(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.unhide_general_forum_topic (
                chat_id=update.effective_chat.id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unhide_general_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().unhide_general_forum_topic(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_menu_button(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> MenuButton:
        """Shortcut for::

             await bot.get_chat_menu_button(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_chat_menu_button`.

        Caution:
            Can only work, if the chat is a private chat.

        .. seealso:: :meth:`set_menu_button`

        .. versionadded:: 20.0

        Returns:
            :class:`telegram.MenuButton`: On success, the current menu button is returned.
        """
        return await self.get_bot().get_chat_menu_button(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
