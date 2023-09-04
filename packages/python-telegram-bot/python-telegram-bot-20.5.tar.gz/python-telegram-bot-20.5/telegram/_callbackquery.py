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
# pylint: disable=redefined-builtin
"""This module contains an object that represents a Telegram CallbackQuery"""
from typing import TYPE_CHECKING, Final, Optional, Sequence, Tuple, Union

from telegram import constants
from telegram._files.location import Location
from telegram._message import Message
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import DVInput, JSONDict, ODVInput, ReplyMarkup

if TYPE_CHECKING:
    from telegram import (
        Bot,
        GameHighScore,
        InlineKeyboardMarkup,
        InputMedia,
        MessageEntity,
        MessageId,
    )


class CallbackQuery(TelegramObject):
    """
    This object represents an incoming callback query from a callback button in an inline keyboard.

    If the button that originated the query was attached to a message sent by the bot, the field
    :attr:`message` will be present. If the button was attached to a message sent via the bot (in
    inline mode), the field :attr:`inline_message_id` will be present.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        * In Python :keyword:`from` is a reserved word. Use :paramref:`from_user` instead.
        * Exactly one of the fields :attr:`data` or :attr:`game_short_name` will be present.
        * After the user presses an inline button, Telegram clients will display a progress bar
          until you call :attr:`answer`. It is, therefore, necessary to react
          by calling :attr:`telegram.Bot.answer_callback_query` even if no notification to the user
          is needed (e.g., without specifying any of the optional parameters).
        * If you're using :attr:`telegram.ext.ExtBot.callback_data_cache`, :attr:`data` may be
          an instance
          of :class:`telegram.ext.InvalidCallbackData`. This will be the case, if the data
          associated with the button triggering the :class:`telegram.CallbackQuery` was already
          deleted or if :attr:`data` was manipulated by a malicious client.

          .. versionadded:: 13.6

    Args:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        chat_instance (:obj:`str`): Global identifier, uniquely corresponding to the chat to which
            the message with the callback button was sent. Useful for high scores in games.
        message (:class:`telegram.Message`, optional): Message with the callback button that
            originated the query. Note that message content and message date will not be available
            if the message is too old.
        data (:obj:`str`, optional): Data associated with the callback button. Be aware that the
            message, which originated the query, can contain no callback buttons with this data.
        inline_message_id (:obj:`str`, optional): Identifier of the message sent via the bot in
            inline mode, that originated the query.
        game_short_name (:obj:`str`, optional): Short name of a Game to be returned, serves as
            the unique identifier for the game.

    Attributes:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        chat_instance (:obj:`str`): Global identifier, uniquely corresponding to the chat to which
            the message with the callback button was sent. Useful for high scores in games.
        message (:class:`telegram.Message`): Optional. Message with the callback button that
            originated the query. Note that message content and message date will not be available
            if the message is too old.
        data (:obj:`str` | :obj:`object`): Optional. Data associated with the callback button.
            Be aware that the message, which originated the query, can contain no callback buttons
            with this data.

            Tip:
                The value here is the same as the value passed in
                :paramref:`telegram.InlineKeyboardButton.callback_data`.
        inline_message_id (:obj:`str`): Optional. Identifier of the message sent via the bot in
            inline mode, that originated the query.
        game_short_name (:obj:`str`): Optional. Short name of a Game to be returned, serves as
            the unique identifier for the game.


    """

    __slots__ = (
        "game_short_name",
        "message",
        "chat_instance",
        "id",
        "from_user",
        "inline_message_id",
        "data",
    )

    def __init__(
        self,
        id: str,
        from_user: User,
        chat_instance: str,
        message: Optional[Message] = None,
        data: Optional[str] = None,
        inline_message_id: Optional[str] = None,
        game_short_name: Optional[str] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.id: str = id  # pylint: disable=invalid-name
        self.from_user: User = from_user
        self.chat_instance: str = chat_instance
        # Optionals
        self.message: Optional[Message] = message
        self.data: Optional[str] = data
        self.inline_message_id: Optional[str] = inline_message_id
        self.game_short_name: Optional[str] = game_short_name

        self._id_attrs = (self.id,)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["CallbackQuery"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["from_user"] = User.de_json(data.pop("from", None), bot)
        data["message"] = Message.de_json(data.get("message"), bot)

        return super().de_json(data=data, bot=bot)

    async def answer(
        self,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.answer_callback_query(update.callback_query.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.answer_callback_query`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().answer_callback_query(
            callback_query_id=self.id,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def edit_message_text(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        entities: Optional[Sequence["MessageEntity"]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            await update.callback_query.message.edit_text(*args, **kwargs)

        or::

            await bot.edit_message_text(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs,
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_text` and :meth:`telegram.Message.edit_text`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return await self.get_bot().edit_message_text(
                inline_message_id=self.inline_message_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                reply_markup=reply_markup,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
                entities=entities,
                chat_id=None,
                message_id=None,
            )
        return await self.message.edit_text(
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            entities=entities,
        )

    async def edit_message_caption(
        self,
        caption: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            await update.callback_query.message.edit_caption(*args, **kwargs)

        or::

            await bot.edit_message_caption(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs,
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_caption` and :meth:`telegram.Message.edit_caption`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return await self.get_bot().edit_message_caption(
                caption=caption,
                inline_message_id=self.inline_message_id,
                reply_markup=reply_markup,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                parse_mode=parse_mode,
                api_kwargs=api_kwargs,
                caption_entities=caption_entities,
                chat_id=None,
                message_id=None,
            )
        return await self.message.edit_caption(
            caption=caption,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            caption_entities=caption_entities,
        )

    async def edit_message_reply_markup(
        self,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            await update.callback_query.message.edit_reply_markup(*args, **kwargs)

        or::

            await bot.edit_message_reply_markup(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_reply_markup` and
        :meth:`telegram.Message.edit_reply_markup`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return await self.get_bot().edit_message_reply_markup(
                reply_markup=reply_markup,
                inline_message_id=self.inline_message_id,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return await self.message.edit_reply_markup(
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def edit_message_media(
        self,
        media: "InputMedia",
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            await update.callback_query.message.edit_media(*args, **kwargs)

        or::

            await bot.edit_message_media(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_media` and :meth:`telegram.Message.edit_media`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return await self.get_bot().edit_message_media(
                inline_message_id=self.inline_message_id,
                media=media,
                reply_markup=reply_markup,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return await self.message.edit_media(
            media=media,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def edit_message_live_location(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        *,
        location: Optional[Location] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            await update.callback_query.message.edit_live_location(*args, **kwargs)

        or::

            await bot.edit_message_live_location(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_live_location` and
        :meth:`telegram.Message.edit_live_location`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return await self.get_bot().edit_message_live_location(
                inline_message_id=self.inline_message_id,
                latitude=latitude,
                longitude=longitude,
                location=location,
                reply_markup=reply_markup,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
                horizontal_accuracy=horizontal_accuracy,
                heading=heading,
                proximity_alert_radius=proximity_alert_radius,
                chat_id=None,
                message_id=None,
            )
        return await self.message.edit_live_location(
            latitude=latitude,
            longitude=longitude,
            location=location,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
        )

    async def stop_message_live_location(
        self,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            await update.callback_query.message.stop_live_location(*args, **kwargs)

        or::

            await bot.stop_message_live_location(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.stop_message_live_location` and
        :meth:`telegram.Message.stop_live_location`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return await self.get_bot().stop_message_live_location(
                inline_message_id=self.inline_message_id,
                reply_markup=reply_markup,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return await self.message.stop_live_location(
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_game_score(
        self,
        user_id: Union[int, str],
        score: int,
        force: Optional[bool] = None,
        disable_edit_message: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

           await update.callback_query.message.set_game_score(*args, **kwargs)

        or::

            await bot.set_game_score(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_game_score` and :meth:`telegram.Message.set_game_score`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return await self.get_bot().set_game_score(
                inline_message_id=self.inline_message_id,
                user_id=user_id,
                score=score,
                force=force,
                disable_edit_message=disable_edit_message,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return await self.message.set_game_score(
            user_id=user_id,
            score=score,
            force=force,
            disable_edit_message=disable_edit_message,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_game_high_scores(
        self,
        user_id: Union[int, str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple["GameHighScore", ...]:
        """Shortcut for either::

            await update.callback_query.message.get_game_high_score(*args, **kwargs)

        or::

            await bot.get_game_high_scores(
                inline_message_id=update.callback_query.inline_message_id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_game_high_scores` and
        :meth:`telegram.Message.get_game_high_scores`.

        Returns:
            Tuple[:class:`telegram.GameHighScore`]

        """
        if self.inline_message_id:
            return await self.get_bot().get_game_high_scores(
                inline_message_id=self.inline_message_id,
                user_id=user_id,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return await self.message.get_game_high_scores(
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def delete_message(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

            await update.callback_query.message.delete(*args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Message.delete`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.message.delete(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def pin_message(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

            await update.callback_query.message.pin(*args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Message.pin`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.message.pin(
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unpin_message(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

            await update.callback_query.message.unpin(*args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Message.unpin`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.message.unpin(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def copy_message(
        self,
        chat_id: Union[int, str],
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

            await update.callback_query.message.copy(
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
                *args,
                **kwargs
            )

        For the documentation of the arguments, please see :meth:`telegram.Message.copy`.

        Returns:
            :class:`telegram.MessageId`: On success, returns the MessageId of the sent message.

        """
        return await self.message.copy(
            chat_id=chat_id,
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

    MAX_ANSWER_TEXT_LENGTH: Final[
        int
    ] = constants.CallbackQueryLimit.ANSWER_CALLBACK_QUERY_TEXT_LENGTH
    """
    :const:`telegram.constants.CallbackQueryLimit.ANSWER_CALLBACK_QUERY_TEXT_LENGTH`

    .. versionadded:: 13.2
    """
