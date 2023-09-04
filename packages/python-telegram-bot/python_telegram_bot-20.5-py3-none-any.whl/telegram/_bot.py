#!/usr/bin/env python
# pylint: disable=no-self-argument, not-callable, no-member, too-many-arguments
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
"""This module contains an object that represents a Telegram Bot."""
import asyncio
import contextlib
import copy
import functools
import pickle
from datetime import datetime
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    no_type_check,
)

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    CRYPTO_INSTALLED = True
except ImportError:
    default_backend = None  # type: ignore[assignment]
    serialization = None  # type: ignore[assignment]
    CRYPTO_INSTALLED = False

from telegram._botcommand import BotCommand
from telegram._botcommandscope import BotCommandScope
from telegram._botdescription import BotDescription, BotShortDescription
from telegram._botname import BotName
from telegram._chat import Chat
from telegram._chatadministratorrights import ChatAdministratorRights
from telegram._chatinvitelink import ChatInviteLink
from telegram._chatmember import ChatMember
from telegram._chatpermissions import ChatPermissions
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.chatphoto import ChatPhoto
from telegram._files.contact import Contact
from telegram._files.document import Document
from telegram._files.file import File
from telegram._files.inputmedia import InputMedia
from telegram._files.inputsticker import InputSticker
from telegram._files.location import Location
from telegram._files.photosize import PhotoSize
from telegram._files.sticker import MaskPosition, Sticker, StickerSet
from telegram._files.venue import Venue
from telegram._files.video import Video
from telegram._files.videonote import VideoNote
from telegram._files.voice import Voice
from telegram._forumtopic import ForumTopic
from telegram._games.gamehighscore import GameHighScore
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresultsbutton import InlineQueryResultsButton
from telegram._menubutton import MenuButton
from telegram._message import Message
from telegram._messageid import MessageId
from telegram._passport.passportelementerrors import PassportElementError
from telegram._payment.shippingoption import ShippingOption
from telegram._poll import Poll
from telegram._sentwebappmessage import SentWebAppMessage
from telegram._telegramobject import TelegramObject
from telegram._update import Update
from telegram._user import User
from telegram._userprofilephotos import UserProfilePhotos
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.files import is_local_file, parse_file_input
from telegram._utils.logging import get_logger
from telegram._utils.types import (
    CorrectOptionID,
    DVInput,
    FileInput,
    JSONDict,
    ODVInput,
    ReplyMarkup,
)
from telegram._utils.warnings import warn
from telegram._webhookinfo import WebhookInfo
from telegram.constants import InlineQueryLimit
from telegram.error import InvalidToken
from telegram.request import BaseRequest, RequestData
from telegram.request._httpxrequest import HTTPXRequest
from telegram.request._requestparameter import RequestParameter
from telegram.warnings import PTBUserWarning

if TYPE_CHECKING:
    from telegram import (
        InlineQueryResult,
        InputFile,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        LabeledPrice,
        MessageEntity,
    )

BT = TypeVar("BT", bound="Bot")


class Bot(TelegramObject, AsyncContextManager["Bot"]):
    """This object represents a Telegram Bot.

    Instances of this class can be used as asyncio context managers, where

    .. code:: python

        async with bot:
            # code

    is roughly equivalent to

    .. code:: python

        try:
            await bot.initialize()
            # code
        finally:
            await bot.shutdown()

    Note:
        * Most bot methods have the argument ``api_kwargs`` which allows passing arbitrary keywords
          to the Telegram API. This can be used to access new features of the API before they are
          incorporated into PTB. However, this is not guaranteed to work, i.e. it will fail for
          passing files.
        * Bots should not be serialized since if you for e.g. change the bots token, then your
          serialized instance will not reflect that change. Trying to pickle a bot instance will
          raise :exc:`pickle.PicklingError`. Trying to deepcopy a bot instance will raise
          :exc:`TypeError`.

    Examples:
        :any:`Raw API Bot <examples.rawapibot>`

    .. seealso:: :wiki:`Your First Bot <Extensions---Your-first-Bot>`,
        :wiki:`Builder Pattern <Builder-Pattern>`

    .. versionadded:: 13.2
        Objects of this class are comparable in terms of equality. Two objects of this class are
        considered equal, if their :attr:`bot` is equal.

    .. versionchanged:: 20.0

        * Removed the deprecated methods ``kick_chat_member``, ``kickChatMember``,
          ``get_chat_members_count`` and ``getChatMembersCount``.
        * Removed the deprecated property ``commands``.
        * Removed the deprecated ``defaults`` parameter. If you want to use
          :class:`telegram.ext.Defaults`, please use the subclass :class:`telegram.ext.ExtBot`
          instead.
        * Attempting to pickle a bot instance will now raise :exc:`pickle.PicklingError`.
        * Attempting to deepcopy a bot instance will now raise :exc:`TypeError`.
        * The following are now keyword-only arguments in Bot methods:
          ``location``, ``filename``, ``venue``, ``contact``,
          ``{read, write, connect, pool}_timeout``, ``api_kwargs``. Use a named argument for those,
          and notice that some positional arguments changed position as a result.
        * For uploading files, file paths are now always accepted. If :paramref:`local_mode` is
          :obj:`False`, the file contents will be read in binary mode and uploaded. Otherwise,
          the file path will be passed in the
          `file URI scheme <https://en.wikipedia.org/wiki/File_URI_scheme>`_.

    .. versionchanged:: 20.5
        Removed deprecated methods ``set_sticker_set_thumb`` and ``setStickerSetThumb``.
        Use :meth:`set_sticker_set_thumbnail` and :meth:`setStickerSetThumbnail` instead.

    Args:
        token (:obj:`str`): Bot's unique authentication token.
        base_url (:obj:`str`, optional): Telegram Bot API service URL.
        base_file_url (:obj:`str`, optional): Telegram Bot API file URL.
        request (:class:`telegram.request.BaseRequest`, optional): Pre initialized
            :class:`telegram.request.BaseRequest` instances. Will be used for all bot methods
            *except* for :meth:`get_updates`. If not passed, an instance of
            :class:`telegram.request.HTTPXRequest` will be used.
        get_updates_request (:class:`telegram.request.BaseRequest`, optional): Pre initialized
            :class:`telegram.request.BaseRequest` instances. Will be used exclusively for
            :meth:`get_updates`. If not passed, an instance of
            :class:`telegram.request.HTTPXRequest` will be used.
        private_key (:obj:`bytes`, optional): Private key for decryption of telegram passport data.
        private_key_password (:obj:`bytes`, optional): Password for above private key.
        local_mode (:obj:`bool`, optional): Set to :obj:`True`, if the :paramref:`base_url` is
            the URI of a `Local Bot API Server <https://core.telegram.org/bots/api#using-a-local\
            -bot-api-server>`_ that runs with the ``--local`` flag. Currently, the only effect of
            this is that files are uploaded using their local path in the
            `file URI scheme <https://en.wikipedia.org/wiki/File_URI_scheme>`_.
            Defaults to :obj:`False`.

            .. versionadded:: 20.0.

    .. include:: inclusions/bot_methods.rst

    .. |removed_thumb_arg| replace:: Removed deprecated argument ``thumb``. Use
        ``thumbnail`` instead.

    """

    # This is a class variable since we want to override the logger name in ExtBot
    # without having to change all places where this is used
    _LOGGER = get_logger(__name__)

    __slots__ = (
        "_token",
        "_base_url",
        "_base_file_url",
        "_private_key",
        "_bot_user",
        "_request",
        "_initialized",
        "_local_mode",
    )

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.telegram.org/bot",
        base_file_url: str = "https://api.telegram.org/file/bot",
        request: Optional[BaseRequest] = None,
        get_updates_request: Optional[BaseRequest] = None,
        private_key: Optional[bytes] = None,
        private_key_password: Optional[bytes] = None,
        local_mode: bool = False,
    ):
        super().__init__(api_kwargs=None)
        if not token:
            raise InvalidToken("You must pass the token you received from https://t.me/Botfather!")
        self._token: str = token

        self._base_url: str = base_url + self._token
        self._base_file_url: str = base_file_url + self._token
        self._local_mode: bool = local_mode
        self._bot_user: Optional[User] = None
        self._private_key: Optional[bytes] = None
        self._initialized: bool = False

        self._request: Tuple[BaseRequest, BaseRequest] = (
            HTTPXRequest() if get_updates_request is None else get_updates_request,
            HTTPXRequest() if request is None else request,
        )

        # this section is about issuing a warning when using HTTP/2 and connect to a self hosted
        # bot api instance, which currently only supports HTTP/1.1. Checking if a custom base url
        # is set is the best way to do that.

        warning_string = ""

        if (
            isinstance(self._request[0], HTTPXRequest)
            and self._request[0].http_version == "2"
            and not base_url.startswith("https://api.telegram.org/bot")
        ):
            warning_string = "get_updates_request"

        if (
            isinstance(self._request[1], HTTPXRequest)
            and self._request[1].http_version == "2"
            and not base_url.startswith("https://api.telegram.org/bot")
        ):
            if warning_string:
                warning_string += " and request"
            else:
                warning_string = "request"

        if warning_string:
            self._warn(
                f"You set the HTTP version for the {warning_string} HTTPXRequest instance to "
                f"HTTP/2. The self hosted bot api instances only support HTTP/1.1. You should "
                f"either run a HTTP proxy in front of it which supports HTTP/2 or use HTTP/1.1.",
                PTBUserWarning,
                stacklevel=2,
            )

        if private_key:
            if not CRYPTO_INSTALLED:
                raise RuntimeError(
                    "To use Telegram Passports, PTB must be installed via `pip install "
                    '"python-telegram-bot[passport]"`.'
                )
            self._private_key = serialization.load_pem_private_key(
                private_key, password=private_key_password, backend=default_backend()
            )

        self._freeze()

    @property
    def token(self) -> str:
        """:obj:`str`: Bot's unique authentication token.

        .. versionadded:: 20.0
        """
        return self._token

    @property
    def base_url(self) -> str:
        """:obj:`str`: Telegram Bot API service URL, built from :paramref:`Bot.base_url` and
        :paramref:`Bot.token`.

        .. versionadded:: 20.0
        """
        return self._base_url

    @property
    def base_file_url(self) -> str:
        """:obj:`str`: Telegram Bot API file URL, built from :paramref:`Bot.base_file_url` and
        :paramref:`Bot.token`.

        .. versionadded:: 20.0
        """
        return self._base_file_url

    @property
    def local_mode(self) -> bool:
        """:obj:`bool`: Whether this bot is running in local mode.

        .. versionadded:: 20.0
        """
        return self._local_mode

    # Proper type hints are difficult because:
    # 1. cryptography doesn't have a nice base class, so it would get lengthy
    # 2. we can't import cryptography if it's not installed
    @property
    def private_key(self) -> Optional[Any]:
        """Deserialized private key for decryption of telegram passport data.

        .. versionadded:: 20.0
        """
        return self._private_key

    @classmethod
    def _warn(
        cls, message: str, category: Type[Warning] = PTBUserWarning, stacklevel: int = 0
    ) -> None:
        """Convenience method to issue a warning. This method is here mostly to make it easier
        for ExtBot to add 1 level to all warning calls.
        """
        warn(message=message, category=category, stacklevel=stacklevel + 1)

    def __reduce__(self) -> NoReturn:
        """Customizes how :func:`copy.deepcopy` processes objects of this type. Bots can not
        be pickled and this method will always raise an exception.

        .. versionadded:: 20.0

        Raises:
            :exc:`pickle.PicklingError`
        """
        raise pickle.PicklingError("Bot objects cannot be pickled!")

    def __deepcopy__(self, memodict: Dict[int, object]) -> NoReturn:
        """Customizes how :func:`copy.deepcopy` processes objects of this type. Bots can not
        be deepcopied and this method will always raise an exception.

        .. versionadded:: 20.0

        Raises:
            :exc:`TypeError`
        """
        raise TypeError("Bot objects cannot be deepcopied!")

    # TODO: After https://youtrack.jetbrains.com/issue/PY-50952 is fixed, we can revisit this and
    # consider adding Paramspec from typing_extensions to properly fix this. Currently a workaround
    def _log(func: Any):  # type: ignore[no-untyped-def] # skipcq: PY-D0003
        @functools.wraps(func)
        async def decorator(self: "Bot", *args: Any, **kwargs: Any) -> Any:
            # pylint: disable=protected-access
            self._LOGGER.debug("Entering: %s", func.__name__)
            result = await func(self, *args, **kwargs)  # skipcq: PYL-E1102
            self._LOGGER.debug(result)
            self._LOGGER.debug("Exiting: %s", func.__name__)
            return result

        return decorator

    def _parse_file_input(
        self,
        file_input: Union[FileInput, "TelegramObject"],
        tg_type: Optional[Type["TelegramObject"]] = None,
        filename: Optional[str] = None,
        attach: bool = False,
    ) -> Union[str, "InputFile", Any]:
        return parse_file_input(
            file_input=file_input,
            tg_type=tg_type,
            filename=filename,
            attach=attach,
            local_mode=self._local_mode,
        )

    def _insert_defaults(self, data: Dict[str, object]) -> None:  # skipcq: PYL-R0201
        """This method is here to make ext.Defaults work. Because we need to be able to tell
        e.g. `send_message(chat_id, text)` from `send_message(chat_id, text, parse_mode=None)`, the
        default values for `parse_mode` etc are not `None` but `DEFAULT_NONE`. While this *could*
        be done in ExtBot instead of Bot, shortcuts like `Message.reply_text` need to work for both
        Bot and ExtBot, so they also have the `DEFAULT_NONE` default values.

        This makes it necessary to convert `DefaultValue(obj)` to `obj` at some point between
        `Message.reply_text` and the request to TG. Doing this here in a centralized manner is a
        rather clean and minimally invasive solution, i.e. the link between tg and tg.ext is as
        small as possible.
        See also _insert_defaults_for_ilq
        ExtBot overrides this method to actually insert default values.

        If in the future we come up with a better way of making `Defaults` work, we can cut this
        link as well.
        """
        # We
        # 1) set the correct parse_mode for all InputMedia objects
        # 2) replace all DefaultValue instances with the corresponding normal value.
        for key, val in data.items():
            # 1)
            if isinstance(val, InputMedia):
                # Copy object as not to edit it in-place
                new = copy.copy(val)
                with new._unfrozen():
                    new.parse_mode = DefaultValue.get_value(new.parse_mode)
                data[key] = new
            elif key == "media" and isinstance(val, Sequence):
                # Copy objects as not to edit them in-place
                copy_list = [copy.copy(media) for media in val]
                for media in copy_list:
                    with media._unfrozen():
                        media.parse_mode = DefaultValue.get_value(media.parse_mode)

                data[key] = copy_list
            # 2)
            else:
                data[key] = DefaultValue.get_value(val)

    async def _post(
        self,
        endpoint: str,
        data: Optional[JSONDict] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Any:
        # We know that the return type is Union[bool, JSONDict, List[JSONDict]], but it's hard
        # to tell mypy which methods expects which of these return values and `Any` saves us a
        # lot of `type: ignore` comments
        if data is None:
            data = {}

        if api_kwargs:
            data.update(api_kwargs)

        # Insert is in-place, so no return value for data
        self._insert_defaults(data)

        # Drop any None values because Telegram doesn't handle them well
        data = {key: value for key, value in data.items() if value is not None}

        return await self._do_post(
            endpoint=endpoint,
            data=data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
        )

    async def _do_post(
        self,
        endpoint: str,
        data: JSONDict,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
    ) -> Union[bool, JSONDict, List[JSONDict]]:
        # This also converts datetimes into timestamps.
        # We don't do this earlier so that _insert_defaults (see above) has a chance to convert
        # to the default timezone in case this is called by ExtBot
        request_data = RequestData(
            parameters=[RequestParameter.from_input(key, value) for key, value in data.items()],
        )

        request = self._request[0] if endpoint == "getUpdates" else self._request[1]

        return await request.post(
            url=f"{self._base_url}/{endpoint}",
            request_data=request_data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
        )

    async def _send_message(
        self,
        endpoint: str,
        data: JSONDict,
        reply_to_message_id: Optional[int] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Any:
        """Protected method to send or edit messages of any type.

        It is here to reduce repetition of if-else closes in the different bot methods,
        i.e. this method takes care of adding its parameters to `data` if appropriate.

        Depending on the bot method, returns either `True` or the message.
        However, it's hard to tell mypy which methods expects which of these return values and
        using `Any` instead saves us a lot of `type: ignore` comments
        """
        # We don't check if (DEFAULT_)None here, so that _post is able to insert the defaults
        # correctly, if necessary
        data["disable_notification"] = disable_notification
        data["allow_sending_without_reply"] = allow_sending_without_reply
        data["protect_content"] = protect_content
        data["parse_mode"] = parse_mode
        data["disable_web_page_preview"] = disable_web_page_preview

        if reply_to_message_id is not None:
            data["reply_to_message_id"] = reply_to_message_id

        if reply_markup is not None:
            data["reply_markup"] = reply_markup

        if message_thread_id is not None:
            data["message_thread_id"] = message_thread_id

        if caption is not None:
            data["caption"] = caption

        if caption_entities is not None:
            data["caption_entities"] = caption_entities

        result = await self._post(
            endpoint,
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        if result is True:
            return result

        return Message.de_json(result, self)

    async def initialize(self) -> None:
        """Initialize resources used by this class. Currently calls :meth:`get_me` to
        cache :attr:`bot` and calls :meth:`telegram.request.BaseRequest.initialize` for
        the request objects used by this bot.

        .. seealso:: :meth:`shutdown`

        .. versionadded:: 20.0
        """
        if self._initialized:
            self._LOGGER.debug("This Bot is already initialized.")
            return

        await asyncio.gather(self._request[0].initialize(), self._request[1].initialize())
        # Since the bot is to be initialized only once, we can also use it for
        # verifying the token passed and raising an exception if it's invalid.
        try:
            await self.get_me()
        except InvalidToken as exc:
            raise InvalidToken(f"The token `{self._token}` was rejected by the server.") from exc
        self._initialized = True

    async def shutdown(self) -> None:
        """Stop & clear resources used by this class. Currently just calls
        :meth:`telegram.request.BaseRequest.shutdown` for the request objects used by this bot.

        .. seealso:: :meth:`initialize`

        .. versionadded:: 20.0
        """
        if not self._initialized:
            self._LOGGER.debug("This Bot is already shut down. Returning.")
            return

        await asyncio.gather(self._request[0].shutdown(), self._request[1].shutdown())
        self._initialized = False

    async def __aenter__(self: BT) -> BT:
        try:
            await self.initialize()
            return self
        except Exception as exc:
            await self.shutdown()
            raise exc

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # Make sure not to return `True` so that exceptions are not suppressed
        # https://docs.python.org/3/reference/datamodel.html?#object.__aexit__
        await self.shutdown()

    @property
    def request(self) -> BaseRequest:
        """The :class:`~telegram.request.BaseRequest` object used by this bot.

        Warning:
            Requests to the Bot API are made by the various methods of this class. This attribute
            should *not* be used manually.
        """
        return self._request[1]

    @property
    def bot(self) -> User:
        """:class:`telegram.User`: User instance for the bot as returned by :meth:`get_me`.

        Warning:
            This value is the cached return value of :meth:`get_me`. If the bots profile is
            changed during runtime, this value won't reflect the changes until :meth:`get_me` is
            called again.

        .. seealso:: :meth:`initialize`
        """
        if self._bot_user is None:
            raise RuntimeError(
                f"{self.__class__.__name__} is not properly initialized. Call "
                f"`{self.__class__.__name__}.initialize` before accessing this property."
            )
        return self._bot_user

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """:obj:`int`: Unique identifier for this bot. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.id

    @property
    def first_name(self) -> str:
        """:obj:`str`: Bot's first name. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.first_name

    @property
    def last_name(self) -> str:
        """:obj:`str`: Optional. Bot's last name. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.last_name  # type: ignore

    @property
    def username(self) -> str:
        """:obj:`str`: Bot's username. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.username  # type: ignore

    @property
    def link(self) -> str:
        """:obj:`str`: Convenience property. Returns the t.me link of the bot."""
        return f"https://t.me/{self.username}"

    @property
    def can_join_groups(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.can_join_groups` attribute. Shortcut for the
        corresponding attribute of :attr:`bot`.
        """
        return self.bot.can_join_groups  # type: ignore

    @property
    def can_read_all_group_messages(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.can_read_all_group_messages` attribute.
        Shortcut for the corresponding attribute of :attr:`bot`.
        """
        return self.bot.can_read_all_group_messages  # type: ignore

    @property
    def supports_inline_queries(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.supports_inline_queries` attribute.
        Shortcut for the corresponding attribute of :attr:`bot`.
        """
        return self.bot.supports_inline_queries  # type: ignore

    @property
    def name(self) -> str:
        """:obj:`str`: Bot's @username. Shortcut for the corresponding attribute of :attr:`bot`."""
        return f"@{self.username}"

    @_log
    async def get_me(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> User:
        """A simple method for testing your bot's auth token. Requires no parameters.

        Returns:
            :class:`telegram.User`: A :class:`telegram.User` instance representing that bot if the
            credentials are valid, :obj:`None` otherwise.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        result = await self._post(
            "getMe",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        self._bot_user = User.de_json(result, self)
        return self._bot_user  # type: ignore[return-value]

    @_log
    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        entities: Optional[Sequence["MessageEntity"]] = None,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Message:
        """Use this method to send text messages.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            text (:obj:`str`): Text of the message to be sent. Max
                :tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`): |parse_mode|
            entities (Sequence[:class:`telegram.MessageEntity`], optional): Sequence of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.

                .. versionchanged:: 20.0
                    |sequenceargs|
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

        Returns:
            :class:`telegram.Message`: On success, the sent message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "text": text, "entities": entities}

        return await self._send_message(
            "sendMessage",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to delete a message, including service messages, with the following
        limitations:

        - A message can only be deleted if it was sent less than 48 hours ago.
        - Service messages about a supergroup, channel, or forum topic creation can't be deleted.
        - A dice message in a private chat can only be deleted if it was sent more than 24
          hours ago.
        - Bots can delete outgoing messages in private chats, groups, and supergroups.
        - Bots can delete incoming messages in private chats.
        - Bots granted :attr:`~telegram.ChatMemberAdministrator.can_post_messages` permissions
          can delete outgoing messages in channels.
        - If the bot is an administrator of a group, it can delete any message there.
        - If the bot has :attr:`~telegram.ChatMemberAdministrator.can_delete_messages`
          permission in a supergroup or a channel, it can delete any message there.

        ..
            The method CallbackQuery.delete_message() will not be found when automatically
            generating "Shortcuts" admonitions for Bot methods because it has no calls
            to Bot methods in its return statement(s). So it is manually included in "See also".

        .. seealso::
            :meth:`telegram.CallbackQuery.delete_message` (calls :meth:`delete_message`
            indirectly, via :meth:`telegram.Message.delete`)

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            message_id (:obj:`int`): Identifier of the message to delete.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "message_id": message_id}
        return await self._post(
            "deleteMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def forward_message(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        Use this method to forward messages of any kind. Service messages can't be forwarded.

        Note:
            Since the release of Bot API 5.5 it can be impossible to forward messages from
            some chats. Use the attributes :attr:`telegram.Message.has_protected_content` and
            :attr:`telegram.Chat.has_protected_content` to check this.

            As a workaround, it is still possible to use :meth:`copy_message`. However, this
            behaviour is undocumented and might be changed by Telegram.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            from_chat_id (:obj:`int` | :obj:`str`): Unique identifier for the chat where the
                original message was sent (or channel username in the format ``@channelusername``).
            message_id (:obj:`int`): Message identifier in the chat specified in
                :paramref:`from_chat_id`.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
        }

        return await self._send_message(
            "forwardMessage",
            data,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_photo(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """Use this method to send photos.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            photo (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.PhotoSize`): Photo to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.

                Caution:
                    * The photo must be at most 10MB in size.
                    * The photo's width and height must not exceed 10000 in total.
                    * Width and height ratio must be at most 20.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Photo caption (may also be used when resending photos
                by file_id), 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH`
                characters after entities parsing.
            parse_mode (:obj:`str`, optional): |parse_mode|
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0
            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            has_spoiler (:obj:`bool`, optional): Pass :obj:`True` if the photo needs to be covered
                with a spoiler animation.

                .. versionadded:: 20.0

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the photo, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "photo": self._parse_file_input(photo, PhotoSize, filename=filename),
            "has_spoiler": has_spoiler,
        }

        return await self._send_message(
            "sendPhoto",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_audio(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        Use this method to send audio files, if you want Telegram clients to display them in the
        music player. Your audio must be in the ``.mp3`` or ``.m4a`` format.

        Bots can currently send audio files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        For sending voice messages, use the :meth:`send_voice` method instead.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        .. versionchanged:: 20.5
            |removed_thumb_arg|

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            audio (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Audio`): Audio file to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Audio` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Audio caption,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): |parse_mode|
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            duration (:obj:`int`, optional): Duration of sent audio in seconds.
            performer (:obj:`str`, optional): Performer.
            title (:obj:`str`, optional): Track name.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionadded:: 20.2

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the audio, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "audio": self._parse_file_input(audio, Audio, filename=filename),
            "duration": duration,
            "performer": performer,
            "title": title,
            "thumbnail": self._parse_file_input(thumbnail, attach=True) if thumbnail else None,
        }

        return await self._send_message(
            "sendAudio",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_document(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        Use this method to send general files.

        Bots can currently send files of any type of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        .. versionchanged:: 20.5
            |removed_thumb_arg|

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            document (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Document`): File to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Document` object to send.

                Note:
                    Sending by URL will currently only work ``GIF``, ``PDF`` & ``ZIP`` files.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Document caption (may also be used when resending
                documents by file_id), 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH`
                characters after entities parsing.
            disable_content_type_detection (:obj:`bool`, optional): Disables automatic server-side
                content type detection for files uploaded using multipart/form-data.
            parse_mode (:obj:`str`, optional): |parse_mode|
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionadded:: 20.2

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the document, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "document": self._parse_file_input(document, Document, filename=filename),
            "disable_content_type_detection": disable_content_type_detection,
            "thumbnail": self._parse_file_input(thumbnail, attach=True) if thumbnail else None,
        }

        return await self._send_message(
            "sendDocument",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_sticker(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        Use this method to send static ``.WEBP``, animated ``.TGS``, or video ``.WEBM`` stickers.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Sticker`): Sticker to send.
                |fileinput| Video stickers can only be sent by a ``file_id``. Animated stickers
                can't be sent via an HTTP URL.

                Lastly you can pass an existing :class:`telegram.Sticker` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            emoji (:obj:`str`, optional): Emoji associated with the sticker; only for just
                uploaded stickers

                .. versionadded:: 20.2
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "sticker": self._parse_file_input(sticker, Sticker),
            "emoji": emoji,
        }
        return await self._send_message(
            "sendSticker",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_video(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """Use this method to send video files, Telegram clients support mp4 videos
        (other formats may be sent as Document).

        Bots can currently send video files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        Note:
            :paramref:`thumbnail` will be ignored for small video files, for which Telegram can
            easily generate thumbnails. However, this behaviour is undocumented and might be
            changed by Telegram.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        .. versionchanged:: 20.5
            |removed_thumb_arg|

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            video (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Video`): Video file to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Video` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            width (:obj:`int`, optional): Video width.
            height (:obj:`int`, optional): Video height.
            caption (:obj:`str`, optional): Video caption (may also be used when resending videos
                by file_id), 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH`
                characters after entities parsing.
            parse_mode (:obj:`str`, optional): |parse_mode|
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            supports_streaming (:obj:`bool`, optional): Pass :obj:`True`, if the uploaded video is
                suitable for streaming.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            has_spoiler (:obj:`bool`, optional): Pass :obj:`True` if the video needs to be covered
                with a spoiler animation.

                .. versionadded:: 20.0
            thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionadded:: 20.2

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the video, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "video": self._parse_file_input(video, Video, filename=filename),
            "duration": duration,
            "width": width,
            "height": height,
            "supports_streaming": supports_streaming,
            "thumbnail": self._parse_file_input(thumbnail, attach=True) if thumbnail else None,
            "has_spoiler": has_spoiler,
        }

        return await self._send_message(
            "sendVideo",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_video_note(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        As of v.4.0, Telegram clients support rounded square mp4 videos of up to 1 minute long.
        Use this method to send video messages.

        Note:
            :paramref:`thumbnail` will be ignored for small video files, for which Telegram can
            easily generate thumbnails. However, this behaviour is undocumented and might be
            changed by Telegram.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        .. versionchanged:: 20.5
            |removed_thumb_arg|

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            video_note (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.VideoNote`): Video note to send.
                Pass a file_id as String to send a video note that exists on the Telegram
                servers (recommended) or upload a new video using multipart/form-data.
                |uploadinput|
                Lastly you can pass an existing :class:`telegram.VideoNote` object to send.
                Sending video notes by a URL is currently unsupported.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            length (:obj:`int`, optional): Video width and height, i.e. diameter of the video
                message.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionadded:: 20.2

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the video note, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "video_note": self._parse_file_input(video_note, VideoNote, filename=filename),
            "duration": duration,
            "length": length,
            "thumbnail": self._parse_file_input(thumbnail, attach=True) if thumbnail else None,
        }

        return await self._send_message(
            "sendVideoNote",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_animation(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound).
        Bots can currently send animation files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        Note:
            :paramref:`thumbnail` will be ignored for small files, for which Telegram can easily
            generate thumbnails. However, this behaviour is undocumented and might be changed
            by Telegram.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        .. versionchanged:: 20.5
            |removed_thumb_arg|

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            animation (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Animation`): Animation to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Animation` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            duration (:obj:`int`, optional): Duration of sent animation in seconds.
            width (:obj:`int`, optional): Animation width.
            height (:obj:`int`, optional): Animation height.
            caption (:obj:`str`, optional): Animation caption (may also be used when resending
                animations by file_id),
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): |parse_mode|
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            has_spoiler (:obj:`bool`, optional): Pass :obj:`True` if the animation needs to be
                covered with a spoiler animation.

                .. versionadded:: 20.0
            thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionadded:: 20.2

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the animation, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "animation": self._parse_file_input(animation, Animation, filename=filename),
            "duration": duration,
            "width": width,
            "height": height,
            "thumbnail": self._parse_file_input(thumbnail, attach=True) if thumbnail else None,
            "has_spoiler": has_spoiler,
        }

        return await self._send_message(
            "sendAnimation",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_voice(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        Use this method to send audio files, if you want Telegram clients to display the file
        as a playable voice message. For this to work, your audio must be in an ``.ogg`` file
        encoded with OPUS (other formats may be sent as Audio or Document). Bots can currently
        send voice messages of up to :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD`
        in size, this limit may be changed in the future.

        Note:
            To use this method, the file must have the type :mimetype:`audio/ogg` and be no more
            than :tg-const:`telegram.constants.FileSizeLimit.VOICE_NOTE_FILE_SIZE` in size.
            :tg-const:`telegram.constants.FileSizeLimit.VOICE_NOTE_FILE_SIZE`-
            :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_DOWNLOAD` voice notes will be
            sent as files.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            voice (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Voice`): Voice file to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Voice` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Voice message caption,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): |parse_mode|
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            duration (:obj:`int`, optional): Duration of the voice message in seconds.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the voice, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "voice": self._parse_file_input(voice, Voice, filename=filename),
            "duration": duration,
        }

        return await self._send_message(
            "sendVoice",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_media_group(
        self,
        chat_id: Union[int, str],
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
    ) -> Tuple[Message, ...]:
        """Use this method to send a group of photos, videos, documents or audios as an album.
        Documents and audio files can be only grouped in an album with messages of the same type.

        Note:
            If you supply a :paramref:`caption` (along with either :paramref:`parse_mode` or
            :paramref:`caption_entities`), then items in :paramref:`media` must have no captions,
            and vice versa.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        .. versionchanged:: 20.0
            Returns a tuple instead of a list.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            media (Sequence[:class:`telegram.InputMediaAudio`,\
                :class:`telegram.InputMediaDocument`, :class:`telegram.InputMediaPhoto`,\
                :class:`telegram.InputMediaVideo`]): An array
                describing messages to be sent, must include
                :tg-const:`telegram.constants.MediaGroupLimit.MIN_MEDIA_LENGTH`-
                :tg-const:`telegram.constants.MediaGroupLimit.MAX_MEDIA_LENGTH` items.

                .. versionchanged:: 20.0
                    |sequenceargs|
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|

        Keyword Args:
            caption (:obj:`str`, optional): Caption that will be added to the
                first element of :paramref:`media`, so that it will be used as caption for the
                whole media group.
                Defaults to :obj:`None`.

                .. versionadded:: 20.0
            parse_mode (:obj:`str` | :obj:`None`, optional):
                Parse mode for :paramref:`caption`.
                See the constants in :class:`telegram.constants.ParseMode` for the
                available modes.

                .. versionadded:: 20.0
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                List of special entities for :paramref:`caption`,
                which can be specified instead of :paramref:`parse_mode`.
                Defaults to :obj:`None`.

                .. versionadded:: 20.0

        Returns:
            Tuple[:class:`telegram.Message`]: An array of the sent Messages.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        if caption and any(
            [
                any(item.caption for item in media),
                any(item.caption_entities for item in media),
                # if parse_mode was set explicitly, even to None, error must be raised
                any(item.parse_mode is not DEFAULT_NONE for item in media),
            ]
        ):
            raise ValueError("You can only supply either group caption or media with captions.")

        if caption:
            # Copy first item (to avoid mutation of original object), apply group caption to it.
            # This will lead to the group being shown with this caption.
            item_to_get_caption = copy.copy(media[0])
            with item_to_get_caption._unfrozen():
                item_to_get_caption.caption = caption
                if parse_mode is not DEFAULT_NONE:
                    item_to_get_caption.parse_mode = parse_mode
                item_to_get_caption.caption_entities = parse_sequence_arg(caption_entities)

            # copy the list (just the references) to avoid mutating the original list
            media = list(media)
            media[0] = item_to_get_caption

        data: JSONDict = {
            "chat_id": chat_id,
            "media": media,
            "disable_notification": disable_notification,
            "allow_sending_without_reply": allow_sending_without_reply,
            "protect_content": protect_content,
            "message_thread_id": message_thread_id,
            "reply_to_message_id": reply_to_message_id,
        }

        result = await self._post(
            "sendMediaGroup",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return Message.de_list(result, self)

    @_log
    async def send_location(
        self,
        chat_id: Union[int, str],
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
        location: Optional[Location] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Message:
        """Use this method to send point on the map.

        Note:
            You can either supply a :paramref:`latitude` and :paramref:`longitude` or a
            :paramref:`location`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            latitude (:obj:`float`, optional): Latitude of location.
            longitude (:obj:`float`, optional): Longitude of location.
            horizontal_accuracy (:obj:`int`, optional): The radius of uncertainty for the location,
                measured in meters;
                0-:tg-const:`telegram.constants.LocationLimit.HORIZONTAL_ACCURACY`.
            live_period (:obj:`int`, optional): Period in seconds for which the location will be
                updated, should be between
                :tg-const:`telegram.constants.LocationLimit.MIN_LIVE_PERIOD` and
                :tg-const:`telegram.constants.LocationLimit.MAX_LIVE_PERIOD`.
            heading (:obj:`int`, optional): For live locations, a direction in which the user is
                moving, in degrees. Must be between
                :tg-const:`telegram.constants.LocationLimit.MIN_HEADING` and
                :tg-const:`telegram.constants.LocationLimit.MAX_HEADING` if specified.
            proximity_alert_radius (:obj:`int`, optional): For live locations, a maximum distance
                for proximity alerts about approaching another chat member, in meters. Must be
                between :tg-const:`telegram.constants.LocationLimit.MIN_PROXIMITY_ALERT_RADIUS`
                and :tg-const:`telegram.constants.LocationLimit.MAX_PROXIMITY_ALERT_RADIUS`
                if specified.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            location (:class:`telegram.Location`, optional): The location to send.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if not ((latitude is not None and longitude is not None) or location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument."
            )

        if not (latitude is not None or longitude is not None) ^ bool(location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument. Not both."
            )

        if isinstance(location, Location):
            latitude = location.latitude
            longitude = location.longitude

        data: JSONDict = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "horizontal_accuracy": horizontal_accuracy,
            "live_period": live_period,
            "heading": heading,
            "proximity_alert_radius": proximity_alert_radius,
        }

        return await self._send_message(
            "sendLocation",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_live_location(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
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
        """Use this method to edit live location messages sent by the bot or via the bot
        (for inline bots). A location can be edited until its :attr:`telegram.Location.live_period`
        expires or editing is explicitly disabled by a call to :meth:`stop_message_live_location`.

        Note:
            You can either supply a :paramref:`latitude` and :paramref:`longitude` or a
            :paramref:`location`.

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if :paramref:`inline_message_id`
                is not specified. |chat_id_channel|
            message_id (:obj:`int`, optional): Required if :paramref:`inline_message_id` is not
                specified. Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if :paramref:`chat_id` and
                :paramref:`message_id` are not specified. Identifier of the inline message.
            latitude (:obj:`float`, optional): Latitude of location.
            longitude (:obj:`float`, optional): Longitude of location.
            horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the
                location, measured in meters;
                0-:tg-const:`telegram.constants.LocationLimit.HORIZONTAL_ACCURACY`.
            heading (:obj:`int`, optional): Direction in which the user is moving, in degrees. Must
                be between :tg-const:`telegram.constants.LocationLimit.MIN_HEADING`
                and :tg-const:`telegram.constants.LocationLimit.MAX_HEADING` if specified.
            proximity_alert_radius (:obj:`int`, optional): Maximum distance for proximity alerts
                about approaching another chat member, in meters. Must be between
                :tg-const:`telegram.constants.LocationLimit.MIN_PROXIMITY_ALERT_RADIUS`
                and :tg-const:`telegram.constants.LocationLimit.MAX_PROXIMITY_ALERT_RADIUS`
                if specified.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                inline keyboard.

        Keyword Args:
            location (:class:`telegram.Location`, optional): The location to send.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.
        """
        # The location parameter is a convenience functionality added by us, so enforcing the
        # mutual exclusivity here is nothing that Telegram would handle anyway
        if not (all([latitude, longitude]) or location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument."
            )
        if not (latitude is not None or longitude is not None) ^ bool(location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument. Not both."
            )

        if isinstance(location, Location):
            latitude = location.latitude
            longitude = location.longitude

        data: JSONDict = {
            "latitude": latitude,
            "longitude": longitude,
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "horizontal_accuracy": horizontal_accuracy,
            "heading": heading,
            "proximity_alert_radius": proximity_alert_radius,
        }

        return await self._send_message(
            "editMessageLiveLocation",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def stop_message_live_location(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """Use this method to stop updating a live location message sent by the bot or via the bot
        (for inline bots) before :paramref:`~telegram.Location.live_period` expires.

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if :paramref:`inline_message_id`
                is not specified. |chat_id_channel|
            message_id (:obj:`int`, optional): Required if :paramref:`inline_message_id` is not
                specified. Identifier of the sent message with live location to stop.
            inline_message_id (:obj:`str`, optional): Required if :paramref:`chat_id` and
                :paramref:`message_id` are not specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                inline keyboard.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
        }

        return await self._send_message(
            "stopMessageLiveLocation",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_venue(
        self,
        chat_id: Union[int, str],
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
        venue: Optional[Venue] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Message:
        """Use this method to send information about a venue.

        Note:
            * You can either supply :paramref:`venue`, or :paramref:`latitude`,
              :paramref:`longitude`, :paramref:`title` and :paramref:`address` and optionally
              :paramref:`foursquare_id` and :paramref:`foursquare_type` or optionally
              :paramref:`google_place_id` and :paramref:`google_place_type`.
            * Foursquare details and Google Place details are mutually exclusive. However, this
              behaviour is undocumented and might be changed by Telegram.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            latitude (:obj:`float`, optional): Latitude of venue.
            longitude (:obj:`float`, optional): Longitude of venue.
            title (:obj:`str`, optional): Name of the venue.
            address (:obj:`str`, optional): Address of the venue.
            foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue.
            foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known.
                (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
                "food/icecream".)
            google_place_id (:obj:`str`, optional): Google Places identifier of the venue.
            google_place_type (:obj:`str`, optional): Google Places type of the venue. (See
                `supported types \
                <https://developers.google.com/maps/documentation/places/web-service/supported_types>`_.)
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            venue (:class:`telegram.Venue`, optional): The venue to send.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        # The venue parameter is a convenience functionality added by us, so enforcing the
        # mutual exclusivity here is nothing that Telegram would handle anyway
        if not (venue or all([latitude, longitude, address, title])):
            raise ValueError(
                "Either venue or latitude, longitude, address and title must be "
                "passed as arguments."
            )
        if not bool(venue) ^ any([latitude, longitude, address, title]):
            raise ValueError(
                "Either venue or latitude, longitude, address and title must be "
                "passed as arguments. Not both."
            )

        if isinstance(venue, Venue):
            latitude = venue.location.latitude
            longitude = venue.location.longitude
            address = venue.address
            title = venue.title
            foursquare_id = venue.foursquare_id
            foursquare_type = venue.foursquare_type
            google_place_id = venue.google_place_id
            google_place_type = venue.google_place_type

        data: JSONDict = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "title": title,
            "foursquare_id": foursquare_id,
            "foursquare_type": foursquare_type,
            "google_place_id": google_place_id,
            "google_place_type": google_place_type,
        }

        return await self._send_message(
            "sendVenue",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_contact(
        self,
        chat_id: Union[int, str],
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
        contact: Optional[Contact] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Message:
        """Use this method to send phone contacts.

        Note:
            You can either supply :paramref:`contact` or :paramref:`phone_number` and
            :paramref:`first_name` with optionally :paramref:`last_name` and optionally
            :paramref:`vcard`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            phone_number (:obj:`str`, optional): Contact's phone number.
            first_name (:obj:`str`, optional): Contact's first name.
            last_name (:obj:`str`, optional): Contact's last name.
            vcard (:obj:`str`, optional): Additional data about the contact in the form of a vCard,
                0-:tg-const:`telegram.constants.ContactLimit.VCARD` bytes.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            contact (:class:`telegram.Contact`, optional): The contact to send.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        # The contact parameter is a convenience functionality added by us, so enforcing the
        # mutual exclusivity here is nothing that Telegram would handle anyway
        if (not contact) and (not all([phone_number, first_name])):
            raise ValueError(
                "Either contact or phone_number and first_name must be passed as arguments."
            )
        if not bool(contact) ^ any([phone_number, first_name]):
            raise ValueError(
                "Either contact or phone_number and first_name must be passed as arguments. "
                "Not both."
            )

        if isinstance(contact, Contact):
            phone_number = contact.phone_number
            first_name = contact.first_name
            last_name = contact.last_name
            vcard = contact.vcard

        data: JSONDict = {
            "chat_id": chat_id,
            "phone_number": phone_number,
            "first_name": first_name,
            "last_name": last_name,
            "vcard": vcard,
        }

        return await self._send_message(
            "sendContact",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_game(
        self,
        chat_id: Union[int, str],
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Message:
        """Use this method to send a game.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat.
            game_short_name (:obj:`str`): Short name of the game, serves as the unique identifier
                for the game. Set up your games via `@BotFather <https://t.me/BotFather>`_.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                inline keyboard. If empty, one "Play game_title" button will be
                shown. If not empty, the first button must launch the game.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "game_short_name": game_short_name}

        return await self._send_message(
            "sendGame",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_chat_action(
        self,
        chat_id: Union[str, int],
        action: str,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method when you need to tell the user that something is happening on the bot's
        side. The status is set for 5 seconds or less (when a message arrives from your bot,
        Telegram clients clear its typing status). Telegram only recommends using this method when
        a response from the bot will take a noticeable amount of time to arrive.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            action(:obj:`str`): Type of action to broadcast. Choose one, depending on what the user
                is about to receive. For convenience look at the constants in
                :class:`telegram.constants.ChatAction`.
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

        Returns:
            :obj:`bool`:  On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "action": action,
            "message_thread_id": message_thread_id,
        }
        return await self._post(
            "sendChatAction",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    def _effective_inline_results(  # skipcq: PYL-R0201
        self,
        results: Union[
            Sequence["InlineQueryResult"], Callable[[int], Optional[Sequence["InlineQueryResult"]]]
        ],
        next_offset: Optional[str] = None,
        current_offset: Optional[str] = None,
    ) -> Tuple[Sequence["InlineQueryResult"], Optional[str]]:
        """
        Builds the effective results from the results input.
        We make this a stand-alone method so tg.ext.ExtBot can wrap it.

        Returns:
            Tuple of 1. the effective results and 2. correct the next_offset

        """
        if current_offset is not None and next_offset is not None:
            raise ValueError("`current_offset` and `next_offset` are mutually exclusive!")

        if current_offset is not None:
            # Convert the string input to integer
            current_offset_int = 0 if not current_offset else int(current_offset)

            # for now set to empty string, stating that there are no more results
            # might change later
            next_offset = ""

            if callable(results):
                callable_output = results(current_offset_int)
                if not callable_output:
                    effective_results: Sequence[InlineQueryResult] = []
                else:
                    effective_results = callable_output
                    # the callback *might* return more results on the next call, so we increment
                    # the page count
                    next_offset = str(current_offset_int + 1)

            elif len(results) > (current_offset_int + 1) * InlineQueryLimit.RESULTS:
                # we expect more results for the next page
                next_offset_int = current_offset_int + 1
                next_offset = str(next_offset_int)
                effective_results = results[
                    current_offset_int
                    * InlineQueryLimit.RESULTS : next_offset_int
                    * InlineQueryLimit.RESULTS
                ]
            else:
                effective_results = results[current_offset_int * InlineQueryLimit.RESULTS :]
        else:
            effective_results = results  # type: ignore[assignment]

        return effective_results, next_offset

    @no_type_check  # mypy doesn't play too well with hasattr
    def _insert_defaults_for_ilq_results(self, res: "InlineQueryResult") -> "InlineQueryResult":
        """The reason why this method exists is similar to the description of _insert_defaults
        The reason why we do this in rather than in _insert_defaults is because converting
        DEFAULT_NONE to NONE *before* calling to_dict() makes it way easier to drop None entries
        from the json data.

        Must return the correct object instead of editing in-place!
        """
        # Copy the objects that need modification to avoid modifying the original object
        copied = False
        if hasattr(res, "parse_mode"):
            res = copy.copy(res)
            copied = True
            with res._unfrozen():
                res.parse_mode = DefaultValue.get_value(res.parse_mode)
        if hasattr(res, "input_message_content") and res.input_message_content:
            if hasattr(res.input_message_content, "parse_mode"):
                if not copied:
                    res = copy.copy(res)
                    copied = True

                with res._unfrozen():
                    res.input_message_content = copy.copy(res.input_message_content)
                with res.input_message_content._unfrozen():
                    res.input_message_content.parse_mode = DefaultValue.get_value(
                        res.input_message_content.parse_mode
                    )
            if hasattr(res.input_message_content, "disable_web_page_preview"):
                if not copied:
                    res = copy.copy(res)

                with res._unfrozen():
                    res.input_message_content = copy.copy(res.input_message_content)
                with res.input_message_content._unfrozen():
                    res.input_message_content.disable_web_page_preview = DefaultValue.get_value(
                        res.input_message_content.disable_web_page_preview
                    )

        return res

    @_log
    async def answer_inline_query(
        self,
        inline_query_id: str,
        results: Union[
            Sequence["InlineQueryResult"], Callable[[int], Optional[Sequence["InlineQueryResult"]]]
        ],
        cache_time: Optional[int] = None,
        is_personal: Optional[bool] = None,
        next_offset: Optional[str] = None,
        button: Optional[InlineQueryResultsButton] = None,
        *,
        current_offset: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to send answers to an inline query. No more than
        :tg-const:`telegram.InlineQuery.MAX_RESULTS` results per query are allowed.

        Warning:
            In most use cases :paramref:`current_offset` should not be passed manually. Instead of
            calling this method directly, use the shortcut :meth:`telegram.InlineQuery.answer` with
            :paramref:`telegram.InlineQuery.answer.auto_pagination` set to :obj:`True`, which will
            take care of passing the correct value.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`


        .. versionchanged:: 20.5
           Removed deprecated arguments ``switch_pm_text`` and ``switch_pm_parameter``.

        Args:
            inline_query_id (:obj:`str`): Unique identifier for the answered query.
            results (List[:class:`telegram.InlineQueryResult`] | Callable): A list of results for
                the inline query. In case :paramref:`current_offset` is passed,
                :paramref:`results` may also be
                a callable that accepts the current page index starting from 0. It must return
                either a list of :class:`telegram.InlineQueryResult` instances or :obj:`None` if
                there are no more results.
            cache_time (:obj:`int`, optional): The maximum amount of time in seconds that the
                result of the inline query may be cached on the server. Defaults to ``300``.
            is_personal (:obj:`bool`, optional): Pass :obj:`True`, if results may be cached on
                the server side only for the user that sent the query. By default,
                results may be returned to any user who sends the same query.
            next_offset (:obj:`str`, optional): Pass the offset that a client should send in the
                next query with the same text to receive more results. Pass an empty string if
                there are no more results or if you don't support pagination. Offset length can't
                exceed :tg-const:`telegram.InlineQuery.MAX_OFFSET_LENGTH` bytes.
            button (:class:`telegram.InlineQueryResultsButton`, optional): A button to be shown
                above the inline query results.

                .. versionadded:: 20.3

        Keyword Args:
            current_offset (:obj:`str`, optional): The :attr:`telegram.InlineQuery.offset` of
                the inline query to answer. If passed, PTB will automatically take care of
                the pagination for you, i.e. pass the correct :paramref:`next_offset` and truncate
                the results list/get the results from the callable you passed.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        effective_results, next_offset = self._effective_inline_results(
            results=results, next_offset=next_offset, current_offset=current_offset
        )

        # Apply defaults
        effective_results = [
            self._insert_defaults_for_ilq_results(result) for result in effective_results
        ]

        data: JSONDict = {
            "inline_query_id": inline_query_id,
            "results": effective_results,
            "next_offset": next_offset,
            "cache_time": cache_time,
            "is_personal": is_personal,
            "button": button,
        }

        return await self._post(
            "answerInlineQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_user_profile_photos(
        self,
        user_id: Union[str, int],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> UserProfilePhotos:
        """Use this method to get a list of profile pictures for a user.

        Args:
            user_id (:obj:`int`): Unique identifier of the target user.
            offset (:obj:`int`, optional): Sequential number of the first photo to be returned.
                By default, all photos are returned.
            limit (:obj:`int`, optional): Limits the number of photos to be retrieved. Values
                between :tg-const:`telegram.constants.UserProfilePhotosLimit.MIN_LIMIT`-
                :tg-const:`telegram.constants.UserProfilePhotosLimit.MAX_LIMIT` are accepted.
                Defaults to ``100``.

        Returns:
            :class:`telegram.UserProfilePhotos`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id, "offset": offset, "limit": limit}

        result = await self._post(
            "getUserProfilePhotos",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return UserProfilePhotos.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def get_file(
        self,
        file_id: Union[
            str, Animation, Audio, ChatPhoto, Document, PhotoSize, Sticker, Video, VideoNote, Voice
        ],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> File:
        """
        Use this method to get basic info about a file and prepare it for downloading. For the
        moment, bots can download files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_DOWNLOAD` in size. The file can then
        be e.g. downloaded with :meth:`telegram.File.download_to_drive`. It is guaranteed that
        the link will be valid for at least 1 hour. When the link expires, a new one can be
        requested by calling get_file again.

        Note:
            This function may not preserve the original file name and MIME type.
            You should save the file's MIME type and name (if available) when the File object
            is received.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        Args:
            file_id (:obj:`str` | :class:`telegram.Animation` | :class:`telegram.Audio` |         \
                     :class:`telegram.ChatPhoto` | :class:`telegram.Document` |                   \
                     :class:`telegram.PhotoSize` | :class:`telegram.Sticker` |                    \
                     :class:`telegram.Video` | :class:`telegram.VideoNote` |                      \
                     :class:`telegram.Voice`):
                Either the file identifier or an object that has a file_id attribute
                to get file information about.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        # Try to get the file_id from the object, if it fails, assume it's a string
        with contextlib.suppress(AttributeError):
            file_id = file_id.file_id  # type: ignore[union-attr]

        data: JSONDict = {"file_id": file_id}

        result = await self._post(
            "getFile",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        file_path = cast(dict, result).get("file_path")
        if file_path and not is_local_file(file_path):
            result["file_path"] = f"{self._base_file_url}/{file_path}"

        return File.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def ban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        until_date: Optional[Union[int, datetime]] = None,
        revoke_messages: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to ban a user from a group, supergroup or a channel. In the case of
        supergroups and channels, the user will not be able to return to the group on their own
        using invite links, etc., unless unbanned first. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

        .. versionadded:: 13.7

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target group or username
                of the target supergroup or channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the user will
                be unbanned, unix time. If user is banned for more than 366 days or less than 30
                seconds from the current time they are considered to be banned forever. Applied
                for supergroups and channels only.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            revoke_messages (:obj:`bool`, optional): Pass :obj:`True` to delete all messages from
                the chat for the user that is being removed. If :obj:`False`, the user will be able
                to see messages in the group that were sent before the user was removed.
                Always :obj:`True` for supergroups and channels.

                .. versionadded:: 13.4

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "user_id": user_id,
            "revoke_messages": revoke_messages,
            "until_date": until_date,
        }

        return await self._post(
            "banChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def ban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to ban a channel chat in a supergroup or a channel. Until the chat is
        unbanned, the owner of the banned chat won't be able to send messages on behalf of **any of
        their channels**. The bot must be an administrator in the supergroup or channel for this
        to work and must have the appropriate administrator rights.

        .. versionadded:: 13.9

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target group or username
                of the target supergroup or channel (in the format ``@channelusername``).
            sender_chat_id (:obj:`int`): Unique identifier of the target sender chat.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "sender_chat_id": sender_chat_id}

        return await self._post(
            "banChatSenderChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        only_if_banned: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to unban a previously kicked user in a supergroup or channel.

        The user will *not* return to the group or channel automatically, but will be able to join
        via link, etc. The bot must be an administrator for this to work. By default, this method
        guarantees that after the call the user is not a member of the chat, but will be able to
        join it. So if the user is a member of the chat they will also be *removed* from the chat.
        If you don't want this, use the parameter :paramref:`only_if_banned`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            user_id (:obj:`int`): Unique identifier of the target user.
            only_if_banned (:obj:`bool`, optional): Do nothing if the user is not banned.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id, "only_if_banned": only_if_banned}

        return await self._post(
            "unbanChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to unban a previously banned channel in a supergroup or channel.
        The bot must be an administrator for this to work and must have the
        appropriate administrator rights.

        .. versionadded:: 13.9

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            sender_chat_id (:obj:`int`): Unique identifier of the target sender chat.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "sender_chat_id": sender_chat_id}

        return await self._post(
            "unbanChatSenderChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def answer_callback_query(
        self,
        callback_query_id: str,
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
        """
        Use this method to send answers to callback queries sent from inline keyboards. The answer
        will be displayed to the user as a notification at the top of the chat screen or as an
        alert.
        Alternatively, the user can be redirected to the specified Game URL. For this option to
        work, you must first create a game for your bot via `@BotFather <https://t.me/BotFather>`_
        and accept the terms. Otherwise, you may use links like t.me/your_bot?start=XXXX that open
        your bot with a parameter.

        Args:
            callback_query_id (:obj:`str`): Unique identifier for the query to be answered.
            text (:obj:`str`, optional): Text of the notification. If not specified, nothing will
                be shown to the user, 0-:tg-const:`telegram.CallbackQuery.MAX_ANSWER_TEXT_LENGTH`
                characters.
            show_alert (:obj:`bool`, optional): If :obj:`True`, an alert will be shown by the
                client instead of a notification at the top of the chat screen. Defaults to
                :obj:`False`.
            url (:obj:`str`, optional): URL that will be opened by the user's client. If you have
                created a Game and accepted the conditions via
                `@BotFather <https://t.me/BotFather>`_, specify the URL that
                opens your game - note that this will only work if the query comes from a callback
                game button. Otherwise, you may use links like t.me/your_bot?start=XXXX that open
                your bot with a parameter.
            cache_time (:obj:`int`, optional): The maximum amount of time in seconds that the
                result of the callback query may be cached client-side. Defaults to 0.

        Returns:
            :obj:`bool` On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "callback_query_id": callback_query_id,
            "cache_time": cache_time,
            "text": text,
            "show_alert": show_alert,
            "url": url,
        }

        return await self._post(
            "answerCallbackQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        entities: Optional[Sequence["MessageEntity"]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit text and game messages.

        Note:
            |editreplymarkup|.

        .. seealso:: :attr:`telegram.Game.text`

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if :paramref:`inline_message_id`
                is not specified. |chat_id_channel|
            message_id (:obj:`int`, optional): Required if :paramref:`inline_message_id` is not
                specified. Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if :paramref:`chat_id` and
                :paramref:`message_id` are not specified. Identifier of the inline message.
            text (:obj:`str`): New text of the message,
                :tg-const:`telegram.constants.MessageLimit.MIN_TEXT_LENGTH`-
                :tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): |parse_mode|
            entities (Sequence[:class:`telegram.MessageEntity`], optional): Sequence of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.

                .. versionchanged:: 20.0
                    |sequenceargs|
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "text": text,
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "entities": entities,
        }

        return await self._send_message(
            "editMessageText",
            data,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_caption(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit captions of messages.

        Note:
            |editreplymarkup|

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. |chat_id_channel|
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            caption (:obj:`str`, optional): New caption of the message,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): |parse_mode|
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
        }

        return await self._send_message(
            "editMessageCaption",
            data,
            reply_markup=reply_markup,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_media(
        self,
        media: "InputMedia",
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit animation, audio, document, photo, or video messages. If a message
        is part of a message album, then it can be edited only to an audio for audio albums, only
        to a document for document albums and to a photo or a video otherwise. When an inline
        message is edited, a new file can't be uploaded; use a previously uploaded file via its
        :attr:`~telegram.File.file_id` or specify a URL.

        Note:
            |editreplymarkup|

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        Args:
            media (:class:`telegram.InputMedia`): An object for a new media content
                of the message.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. |chat_id_channel|
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited Message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "media": media,
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
        }

        return await self._send_message(
            "editMessageMedia",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_reply_markup(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit only the reply markup of messages sent by the bot or via the bot
        (for inline bots).

        Note:
            |editreplymarkup|

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. |chat_id_channel|
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
        }

        return await self._send_message(
            "editMessageReplyMarkup",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        allowed_updates: Optional[Sequence[str]] = None,
        *,
        read_timeout: float = 2,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple[Update, ...]:
        """Use this method to receive incoming updates using long polling.

        Note:
            1. This method will not work if an outgoing webhook is set up.
            2. In order to avoid getting duplicate updates, recalculate offset after each
               server response.
            3. To take full advantage of this library take a look at :class:`telegram.ext.Updater`

        .. seealso:: :meth:`telegram.ext.Application.run_polling`,
            :meth:`telegram.ext.Updater.start_polling`

        .. versionchanged:: 20.0
            Returns a tuple instead of a list.

        Args:
            offset (:obj:`int`, optional): Identifier of the first update to be returned. Must be
                greater by one than the highest among the identifiers of previously received
                updates. By default, updates starting with the earliest unconfirmed update are
                returned. An update is considered confirmed as soon as this method is called with
                an offset higher than its :attr:`telegram.Update.update_id`. The negative offset
                can be specified to retrieve updates starting from -offset update from the end of
                the updates queue. All previous updates will be forgotten.
            limit (:obj:`int`, optional): Limits the number of updates to be retrieved. Values
                between :tg-const:`telegram.constants.PollingLimit.MIN_LIMIT`-
                :tg-const:`telegram.constants.PollingLimit.MAX_LIMIT` are accepted.
                Defaults to ``100``.
            timeout (:obj:`int`, optional): Timeout in seconds for long polling. Defaults to ``0``,
                i.e. usual short polling. Should be positive, short polling should be used for
                testing purposes only.
            allowed_updates (Sequence[:obj:`str`]), optional): A sequence the types of
                updates you want your bot to receive. For example, specify ["message",
                "edited_channel_post", "callback_query"] to only receive updates of these types.
                See :class:`telegram.Update` for a complete list of available update types.
                Specify an empty sequence to receive all updates except
                :attr:`telegram.Update.chat_member` (default). If not specified, the previous
                setting will be used. Please note that this parameter doesn't affect updates
                created before the call to the get_updates, so unwanted updates may be received for
                a short period of time.

                .. versionchanged:: 20.0
                    |sequenceargs|

        Returns:
            Tuple[:class:`telegram.Update`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "timeout": timeout,
            "offset": offset,
            "limit": limit,
            "allowed_updates": allowed_updates,
        }

        # Ideally we'd use an aggressive read timeout for the polling. However,
        # * Short polling should return within 2 seconds.
        # * Long polling poses a different problem: the connection might have been dropped while
        #   waiting for the server to return and there's no way of knowing the connection had been
        #   dropped in real time.
        result = cast(
            List[JSONDict],
            await self._post(
                "getUpdates",
                data,
                read_timeout=read_timeout + timeout if timeout else read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
            ),
        )

        if result:
            self._LOGGER.debug("Getting updates: %s", [u["update_id"] for u in result])
        else:
            self._LOGGER.debug("No new updates found.")

        return Update.de_list(result, self)

    @_log
    async def set_webhook(
        self,
        url: str,
        certificate: Optional[FileInput] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[Sequence[str]] = None,
        ip_address: Optional[str] = None,
        drop_pending_updates: Optional[bool] = None,
        secret_token: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, Telegram will send an HTTPS POST request to the
        specified url, containing An Update. In case of an unsuccessful request,
        Telegram will give up after a reasonable amount of attempts.

        If you'd like to make sure that the Webhook was set by you, you can specify secret data in
        the parameter :paramref:`secret_token`. If specified, the request will contain a header
        ``X-Telegram-Bot-Api-Secret-Token`` with the secret token as content.

        Note:
            1. You will not be able to receive updates using :meth:`get_updates` for long as an
               outgoing webhook is set up.
            2. To use a self-signed certificate, you need to upload your public key certificate
               using :paramref:`certificate` parameter. Please upload as
               :class:`~telegram.InputFile`, sending a String will not work.
            3. Ports currently supported for Webhooks:
               :attr:`telegram.constants.SUPPORTED_WEBHOOK_PORTS`.

            If you're having any trouble setting up webhooks, please check out this `guide to
            Webhooks`_.

        Note:
            1. You will not be able to receive updates using :meth:`get_updates` for long as an
               outgoing webhook is set up.
            2. To use a self-signed certificate, you need to upload your public key certificate
               using certificate parameter. Please upload as InputFile, sending a String will not
               work.
            3. Ports currently supported for Webhooks:
               :attr:`telegram.constants.SUPPORTED_WEBHOOK_PORTS`.

            If you're having any trouble setting up webhooks, please check out this `guide to
            Webhooks`_.

        .. seealso:: :meth:`telegram.ext.Application.run_webhook`,
            :meth:`telegram.ext.Updater.start_webhook`

        Examples:
            :any:`Custom Webhook Bot <examples.customwebhookbot>`

        Args:
            url (:obj:`str`): HTTPS url to send updates to. Use an empty string to remove webhook
                integration.
            certificate (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`):
                Upload your public key certificate so that the root
                certificate in use can be checked. See our :wiki:`self-signed guide\
                <Webhooks#creating-a-self-signed-certificate-using-openssl>` for details.
                |uploadinputnopath|
            ip_address (:obj:`str`, optional): The fixed IP address which will be used to send
                webhook requests instead of the IP address resolved through DNS.
            max_connections (:obj:`int`, optional): Maximum allowed number of simultaneous HTTPS
                connections to the webhook for update delivery,
                :tg-const:`telegram.constants.WebhookLimit.MIN_CONNECTIONS_LIMIT`-
                :tg-const:`telegram.constants.WebhookLimit.MAX_CONNECTIONS_LIMIT`.
                Defaults to ``40``. Use lower values to limit the load on your bot's server,
                and higher values to increase your bot's throughput.
            allowed_updates (Sequence[:obj:`str`], optional): A sequence of the types of
                updates you want your bot to receive. For example, specify ["message",
                "edited_channel_post", "callback_query"] to only receive updates of these types.
                See :class:`telegram.Update` for a complete list of available update types.
                Specify an empty sequence to receive all updates except
                :attr:`telegram.Update.chat_member` (default). If not specified, the previous
                setting will be used. Please note that this parameter doesn't affect updates
                created before the call to the set_webhook, so unwanted updates may be received for
                a short period of time.

                .. versionchanged:: 20.0
                    |sequenceargs|
            drop_pending_updates (:obj:`bool`, optional): Pass :obj:`True` to drop all pending
                updates.
            secret_token (:obj:`str`, optional): A secret token to be sent in a header
                ``X-Telegram-Bot-Api-Secret-Token`` in every webhook request,
                :tg-const:`telegram.constants.WebhookLimit.MIN_SECRET_TOKEN_LENGTH`-
                :tg-const:`telegram.constants.WebhookLimit.MAX_SECRET_TOKEN_LENGTH` characters.
                Only characters ``A-Z``, ``a-z``, ``0-9``, ``_`` and ``-`` are allowed.
                The header is useful to ensure that the request comes from a webhook set by you.

                .. versionadded:: 20.0

        Returns:
            :obj:`bool` On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        .. _`guide to Webhooks`: https://core.telegram.org/bots/webhooks

        """
        data: JSONDict = {
            "url": url,
            "max_connections": max_connections,
            "allowed_updates": allowed_updates,
            "ip_address": ip_address,
            "drop_pending_updates": drop_pending_updates,
            "secret_token": secret_token,
            "certificate": self._parse_file_input(certificate),  # type: ignore[arg-type]
        }

        return await self._post(
            "setWebhook",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_webhook(
        self,
        drop_pending_updates: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to remove webhook integration if you decide to switch back to
        :meth:`get_updates()`.

        Args:
            drop_pending_updates (:obj:`bool`, optional): Pass :obj:`True` to drop all pending
                updates.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data = {"drop_pending_updates": drop_pending_updates}

        return await self._post(
            "deleteWebhook",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def leave_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method for your bot to leave a group, supergroup or channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        return await self._post(
            "leaveChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Chat:
        """
        Use this method to get up to date information about the chat (current name of the user for
        one-on-one conversations, current username of a user, group or channel, etc.).

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

        Returns:
            :class:`telegram.Chat`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        result = await self._post(
            "getChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return Chat.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def get_chat_administrators(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple[ChatMember, ...]:
        """
        Use this method to get a list of administrators in a chat.

        .. versionchanged:: 20.0
            Returns a tuple instead of a list.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

        Returns:
            Tuple[:class:`telegram.ChatMember`]: On success, returns a tuple of ``ChatMember``
            objects that contains information about all chat administrators except
            other bots. If the chat is a group or a supergroup and no administrators were
            appointed, only the creator will be returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        result = await self._post(
            "getChatAdministrators",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return ChatMember.de_list(result, self)

    @_log
    async def get_chat_member_count(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> int:
        """Use this method to get the number of members in a chat.

        .. versionadded:: 13.7

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

        Returns:
            :obj:`int`: Number of members in the chat.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        return await self._post(
            "getChatMemberCount",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> ChatMember:
        """Use this method to get information about a member of a chat. The method is only
        guaranteed to work for other users if the bot is an administrator in the chat.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            user_id (:obj:`int`): Unique identifier of the target user.

        Returns:
            :class:`telegram.ChatMember`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}
        result = await self._post(
            "getChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return ChatMember.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def set_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        sticker_set_name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to set a new group sticker set for a supergroup.
        The bot must be an administrator in the chat for this to work and must have the appropriate
        admin rights. Use the field :attr:`telegram.Chat.can_set_sticker_set` optionally returned
        in :meth:`get_chat` requests to check if the bot can use this method.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            sticker_set_name (:obj:`str`): Name of the sticker set to be set as the group
                sticker set.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        data: JSONDict = {"chat_id": chat_id, "sticker_set_name": sticker_set_name}
        return await self._post(
            "setChatStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to delete a group sticker set from a supergroup. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.
        Use the field :attr:`telegram.Chat.can_set_sticker_set` optionally returned in
        :meth:`get_chat` requests to check if the bot can use this method.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|

        Returns:
             :obj:`bool`: On success, :obj:`True` is returned.
        """
        data: JSONDict = {"chat_id": chat_id}
        return await self._post(
            "deleteChatStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_webhook_info(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> WebhookInfo:
        """Use this method to get current webhook status. Requires no parameters.

        If the bot is using :meth:`get_updates`, will return an object with the
        :attr:`telegram.WebhookInfo.url` field empty.

        Returns:
            :class:`telegram.WebhookInfo`

        """
        result = await self._post(
            "getWebhookInfo",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return WebhookInfo.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def set_game_score(
        self,
        user_id: Union[int, str],
        score: int,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        force: Optional[bool] = None,
        disable_edit_message: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Union[Message, bool]:
        """
        Use this method to set the score of the specified user in a game message.

        .. seealso:: :attr:`telegram.Game.text`

        Args:
            user_id (:obj:`int`): User identifier.
            score (:obj:`int`): New score, must be non-negative.
            force (:obj:`bool`, optional): Pass :obj:`True`, if the high score is allowed to
                decrease. This can be useful when fixing mistakes or banning cheaters.
            disable_edit_message (:obj:`bool`, optional): Pass :obj:`True`, if the game message
                should not be automatically edited to include the current scoreboard.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if :paramref:`inline_message_id`
                is not specified. Unique identifier for the target chat.
            message_id (:obj:`int`, optional): Required if :paramref:`inline_message_id` is not
                specified. Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if :paramref:`chat_id` and
                :paramref:`message_id` are not specified. Identifier of the inline message.

        Returns:
            :class:`telegram.Message`: The edited message. If the message is not an inline message
            , :obj:`True`.

        Raises:
            :class:`telegram.error.TelegramError`: If the new score is not greater than the user's
                current score in the chat and :paramref:`force` is :obj:`False`.

        """
        data: JSONDict = {
            "user_id": user_id,
            "score": score,
            "force": force,
            "disable_edit_message": disable_edit_message,
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
        }

        return await self._send_message(
            "setGameScore",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_game_high_scores(
        self,
        user_id: Union[int, str],
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple[GameHighScore, ...]:
        """
        Use this method to get data for high score tables. Will return the score of the specified
        user and several of their neighbors in a game.

        Note:
            This method will currently return scores for the target user, plus two of their
            closest neighbors on each side. Will also return the top three users if the user and
            his neighbors are not among them. Please note that this behavior is subject to change.

        .. versionchanged:: 20.0
            Returns a tuple instead of a list.

        Args:
            user_id (:obj:`int`): Target user id.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if :paramref:`inline_message_id`
                is not specified. Unique identifier for the target chat.
            message_id (:obj:`int`, optional): Required if :paramref:`inline_message_id` is not
                specified. Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if :paramref:`chat_id` and
                :paramref:`message_id` are not specified. Identifier of the inline message.

        Returns:
            Tuple[:class:`telegram.GameHighScore`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "user_id": user_id,
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
        }

        result = await self._post(
            "getGameHighScores",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return GameHighScore.de_list(result, self)

    @_log
    async def send_invoice(
        self,
        chat_id: Union[int, str],
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
        reply_markup: Optional[InlineKeyboardMarkup] = None,
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
    ) -> Message:
        """Use this method to send invoices.

        Warning:
            As of API 5.2 :paramref:`start_parameter` is an optional argument and therefore the
            order of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter :paramref:`start_parameter` is optional.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            title (:obj:`str`): Product name. :tg-const:`telegram.Invoice.MIN_TITLE_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_TITLE_LENGTH` characters.
            description (:obj:`str`): Product description.
                :tg-const:`telegram.Invoice.MIN_DESCRIPTION_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_DESCRIPTION_LENGTH` characters.
            payload (:obj:`str`): Bot-defined invoice payload.
                :tg-const:`telegram.Invoice.MIN_PAYLOAD_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_PAYLOAD_LENGTH` bytes. This will not be
                displayed to the user, use for your internal processes.
            provider_token (:obj:`str`): Payments provider token, obtained via
                `@BotFather <https://t.me/BotFather>`_.
            currency (:obj:`str`): Three-letter ISO 4217 currency code, see `more on currencies
                <https://core.telegram.org/bots/payments#supported-currencies>`_.
            prices (Sequence[:class:`telegram.LabeledPrice`)]: Price breakdown, a sequence
                of components (e.g. product price, tax, discount, delivery cost, delivery tax,
                bonus, etc.).

                .. versionchanged:: 20.0
                    |sequenceargs|
            max_tip_amount (:obj:`int`, optional): The maximum accepted amount for tips in the
                *smallest* units of the currency (integer, **not** float/double). For example, for
                a maximum tip of US$ 1.45 pass ``max_tip_amount = 145``. See the exp parameter in
                `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it
                shows the number of digits past the decimal point for each currency (2 for the
                majority of currencies). Defaults to ``0``.

                .. versionadded:: 13.5
            suggested_tip_amounts (Sequence[:obj:`int`], optional): An array of
                suggested amounts of tips in the *smallest* units of the currency (integer, **not**
                float/double). At most :tg-const:`telegram.Invoice.MAX_TIP_AMOUNTS` suggested tip
                amounts can be specified. The suggested tip amounts must be positive, passed in a
                strictly increased order and must not exceed :paramref:`max_tip_amount`.

                .. versionadded:: 13.5

                .. versionchanged:: 20.0
                    |sequenceargs|
            start_parameter (:obj:`str`, optional): Unique deep-linking parameter. If left empty,
                *forwarded copies* of the sent message will have a *Pay* button, allowing
                multiple users to pay directly from the forwarded message, using the same invoice.
                If non-empty, forwarded copies of the sent message will have a *URL* button with a
                deep link to the bot (instead of a *Pay* button), with the value used as the
                start parameter.

                .. versionchanged:: 13.5
                    As of Bot API 5.2, this parameter is optional.
            provider_data (:obj:`str` | :obj:`object`, optional): data about the
                invoice, which will be shared with the payment provider. A detailed description of
                required fields should be provided by the payment provider. When an object is
                passed, it will be encoded as JSON.
            photo_url (:obj:`str`, optional): URL of the product photo for the invoice. Can be a
                photo of the goods or a marketing image for a service. People like it better when
                they see what they are paying for.
            photo_size (:obj:`str`, optional): Photo size.
            photo_width (:obj:`int`, optional): Photo width.
            photo_height (:obj:`int`, optional): Photo height.
            need_name (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's full
                name to complete the order.
            need_phone_number (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's
                phone number to complete the order.
            need_email (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's email
                to complete the order.
            need_shipping_address (:obj:`bool`, optional): Pass :obj:`True`, if you require the
                user's shipping address to complete the order.
            send_phone_number_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's
                phone number should be sent to provider.
            send_email_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's email
                address should be sent to provider.
            is_flexible (:obj:`bool`, optional): Pass :obj:`True`, if the final price depends on
                the shipping method.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard. If empty, one 'Pay total price' button will be
                shown. If not empty, the first button must be a Pay button.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": currency,
            "prices": prices,
            "max_tip_amount": max_tip_amount,
            "suggested_tip_amounts": suggested_tip_amounts,
            "start_parameter": start_parameter,
            "provider_data": provider_data,
            "photo_url": photo_url,
            "photo_size": photo_size,
            "photo_width": photo_width,
            "photo_height": photo_height,
            "need_name": need_name,
            "need_phone_number": need_phone_number,
            "need_email": need_email,
            "need_shipping_address": need_shipping_address,
            "is_flexible": is_flexible,
            "send_phone_number_to_provider": send_phone_number_to_provider,
            "send_email_to_provider": send_email_to_provider,
        }

        return await self._send_message(
            "sendInvoice",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def answer_shipping_query(  # pylint: disable=invalid-name
        self,
        shipping_query_id: str,
        ok: bool,
        shipping_options: Optional[Sequence[ShippingOption]] = None,
        error_message: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        If you sent an invoice requesting a shipping address and the parameter
        :paramref:`send_invoice.is_flexible` was specified, the Bot API will send an
        :class:`telegram.Update` with a :attr:`telegram.Update.shipping_query` field to the bot.
        Use this method to reply to shipping queries.

        Args:
            shipping_query_id (:obj:`str`): Unique identifier for the query to be answered.
            ok (:obj:`bool`): Specify :obj:`True` if delivery to the specified address is possible
                and :obj:`False` if there are any problems (for example, if delivery to the
                specified address is not possible).
            shipping_options (Sequence[:class:`telegram.ShippingOption`]), optional): Required if
                :paramref:`ok` is :obj:`True`. A sequence of available shipping options.

                .. versionchanged:: 20.0
                    |sequenceargs|
            error_message (:obj:`str`, optional): Required if :paramref:`ok` is :obj:`False`.
                Error message in human readable form that explains why it is impossible to complete
                the order (e.g. "Sorry, delivery to your desired address is unavailable"). Telegram
                will display this message to the user.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "shipping_query_id": shipping_query_id,
            "ok": ok,
            "shipping_options": shipping_options,
            "error_message": error_message,
        }

        return await self._post(
            "answerShippingQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def answer_pre_checkout_query(  # pylint: disable=invalid-name
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Once the user has confirmed their payment and shipping details, the Bot API sends the final
        confirmation in the form of an :class:`telegram.Update` with the field
        :attr:`telegram.Update.pre_checkout_query`. Use this method to respond to such pre-checkout
        queries.

        Note:
            The Bot API must receive an answer within 10 seconds after the pre-checkout
            query was sent.

        Args:
            pre_checkout_query_id (:obj:`str`): Unique identifier for the query to be answered.
            ok (:obj:`bool`): Specify :obj:`True` if everything is alright
                (goods are available, etc.) and the bot is ready to proceed with the order. Use
                :obj:`False` if there are any problems.
            error_message (:obj:`str`, optional): Required if :paramref:`ok` is :obj:`False`. Error
                message in human readable form that explains the reason for failure to proceed with
                the checkout (e.g. "Sorry, somebody just bought the last of our amazing black
                T-shirts while you were busy filling out your payment details. Please choose a
                different color or garment!"). Telegram will display this message to the user.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok,
            "error_message": error_message,
        }

        return await self._post(
            "answerPreCheckoutQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def answer_web_app_query(
        self,
        web_app_query_id: str,
        result: "InlineQueryResult",
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> SentWebAppMessage:
        """Use this method to set the result of an interaction with a Web App and send a
        corresponding message on behalf of the user to the chat from which the query originated.

        .. versionadded:: 20.0

        Args:
            web_app_query_id (:obj:`str`): Unique identifier for the query to be answered.
            result (:class:`telegram.InlineQueryResult`): An object describing the message to be
                sent.

        Returns:
            :class:`telegram.SentWebAppMessage`: On success, a sent
            :class:`telegram.SentWebAppMessage` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "web_app_query_id": web_app_query_id,
            "result": self._insert_defaults_for_ilq_results(result),
        }

        api_result = await self._post(
            "answerWebAppQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return SentWebAppMessage.de_json(api_result, self)  # type: ignore[return-value]

    @_log
    async def restrict_chat_member(
        self,
        chat_id: Union[str, int],
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
        """
        Use this method to restrict a user in a supergroup. The bot must be an administrator in
        the supergroup for this to work and must have the appropriate admin rights. Pass
        :obj:`True` for all boolean parameters to lift restrictions from a user.

        .. seealso:: :meth:`telegram.ChatPermissions.all_permissions`

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            user_id (:obj:`int`): Unique identifier of the target user.
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when restrictions
                will be lifted for the user, unix time. If user is restricted for more than 366
                days or less than 30 seconds from the current time, they are considered to be
                restricted forever.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            permissions (:class:`telegram.ChatPermissions`): An object for new user
                permissions.
            use_independent_chat_permissions (:obj:`bool`, optional): Pass :obj:`True` if chat
                permissions are set independently. Otherwise, the
                :attr:`~telegram.ChatPermissions.can_send_other_messages` and
                :attr:`~telegram.ChatPermissions.can_add_web_page_previews` permissions will imply
                the :attr:`~telegram.ChatPermissions.can_send_messages`,
                :attr:`~telegram.ChatPermissions.can_send_audios`,
                :attr:`~telegram.ChatPermissions.can_send_documents`,
                :attr:`~telegram.ChatPermissions.can_send_photos`,
                :attr:`~telegram.ChatPermissions.can_send_videos`,
                :attr:`~telegram.ChatPermissions.can_send_video_notes`, and
                :attr:`~telegram.ChatPermissions.can_send_voice_notes` permissions; the
                :attr:`~telegram.ChatPermissions.can_send_polls` permission will imply the
                :attr:`~telegram.ChatPermissions.can_send_messages` permission.

                .. versionadded: 20.1

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "user_id": user_id,
            "permissions": permissions,
            "until_date": until_date,
            "use_independent_chat_permissions": use_independent_chat_permissions,
        }

        return await self._post(
            "restrictChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def promote_chat_member(
        self,
        chat_id: Union[str, int],
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
        """
        Use this method to promote or demote a user in a supergroup or a channel. The bot must be
        an administrator in the chat for this to work and must have the appropriate admin rights.
        Pass :obj:`False` for all boolean parameters to demote a user.

        .. versionchanged:: 20.0
           The argument ``can_manage_voice_chats`` was renamed to
           :paramref:`can_manage_video_chats` in accordance to Bot API 6.0.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            user_id (:obj:`int`): Unique identifier of the target user.
            is_anonymous (:obj:`bool`, optional): Pass :obj:`True`, if the administrator's presence
                in the chat is hidden.
            can_manage_chat (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                access the chat event log, chat statistics, message statistics in channels, see
                channel members, see anonymous administrators in supergroups and ignore slow mode.
                Implied by any other administrator privilege.

                .. versionadded:: 13.4

            can_manage_video_chats (:obj:`bool`, optional): Pass :obj:`True`, if the administrator
                can manage video chats.

                .. versionadded:: 20.0

            can_change_info (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                change chat title, photo and other settings.
            can_post_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                create channel posts, channels only.
            can_edit_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                edit messages of other users and can pin messages, channels only.
            can_delete_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                delete messages of other users.
            can_invite_users (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                invite new users to the chat.
            can_restrict_members (:obj:`bool`, optional): Pass :obj:`True`, if the administrator
                can restrict, ban or unban chat members.
            can_pin_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                pin messages, supergroups only.
            can_promote_members (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                add new administrators with a subset of their own privileges or demote
                administrators that they have promoted, directly or indirectly
                (promoted by administrators that were appointed by the user).
            can_manage_topics (:obj:`bool`, optional): Pass :obj:`True`, if the user is
                allowed to create, rename, close, and reopen forum topics; supergroups only.

                .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "user_id": user_id,
            "is_anonymous": is_anonymous,
            "can_change_info": can_change_info,
            "can_post_messages": can_post_messages,
            "can_edit_messages": can_edit_messages,
            "can_delete_messages": can_delete_messages,
            "can_invite_users": can_invite_users,
            "can_restrict_members": can_restrict_members,
            "can_pin_messages": can_pin_messages,
            "can_promote_members": can_promote_members,
            "can_manage_chat": can_manage_chat,
            "can_manage_video_chats": can_manage_video_chats,
            "can_manage_topics": can_manage_topics,
        }

        return await self._post(
            "promoteChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_chat_permissions(
        self,
        chat_id: Union[str, int],
        permissions: ChatPermissions,
        use_independent_chat_permissions: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to set default chat permissions for all members. The bot must be an
        administrator in the group or a supergroup for this to work and must have the
        :attr:`telegram.ChatMemberAdministrator.can_restrict_members` admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            permissions (:class:`telegram.ChatPermissions`): New default chat permissions.
            use_independent_chat_permissions (:obj:`bool`, optional): Pass :obj:`True` if chat
                permissions are set independently. Otherwise, the
                :attr:`~telegram.ChatPermissions.can_send_other_messages` and
                :attr:`~telegram.ChatPermissions.can_add_web_page_previews` permissions will imply
                the :attr:`~telegram.ChatPermissions.can_send_messages`,
                :attr:`~telegram.ChatPermissions.can_send_audios`,
                :attr:`~telegram.ChatPermissions.can_send_documents`,
                :attr:`~telegram.ChatPermissions.can_send_photos`,
                :attr:`~telegram.ChatPermissions.can_send_videos`,
                :attr:`~telegram.ChatPermissions.can_send_video_notes`, and
                :attr:`~telegram.ChatPermissions.can_send_voice_notes` permissions; the
                :attr:`~telegram.ChatPermissions.can_send_polls` permission will imply the
                :attr:`~telegram.ChatPermissions.can_send_messages` permission.

                .. versionadded: 20.1

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "permissions": permissions,
            "use_independent_chat_permissions": use_independent_chat_permissions,
        }
        return await self._post(
            "setChatPermissions",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_chat_administrator_custom_title(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str],
        custom_title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to set a custom title for administrators promoted by the bot in a
        supergroup. The bot must be an administrator for this to work.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            user_id (:obj:`int`): Unique identifier of the target administrator.
            custom_title (:obj:`str`): New custom title for the administrator;
                0-:tg-const:`telegram.constants.ChatLimit.CHAT_ADMINISTRATOR_CUSTOM_TITLE_LENGTH`
                characters, emoji are not allowed.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id, "custom_title": custom_title}

        return await self._post(
            "setChatAdministratorCustomTitle",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def export_chat_invite_link(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> str:
        """
        Use this method to generate a new primary invite link for a chat; any previously generated
        link is revoked. The bot must be an administrator in the chat for this to work and must
        have the appropriate admin rights.

        Note:
            Each administrator in a chat generates their own invite links. Bots can't use invite
            links generated by other administrators. If you want your bot to work with invite
            links, it will need to generate its own link using :meth:`export_chat_invite_link` or
            by calling the :meth:`get_chat` method. If your bot needs to generate a new primary
            invite link replacing its previous one, use :meth:`export_chat_invite_link` again.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

        Returns:
            :obj:`str`: New invite link on success.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        return await self._post(
            "exportChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def create_chat_invite_link(
        self,
        chat_id: Union[str, int],
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
    ) -> ChatInviteLink:
        """
        Use this method to create an additional invite link for a chat. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.
        The link can be revoked using the method :meth:`revoke_chat_invite_link`.

        Note:
            When joining *public* groups via an invite link, Telegram clients may display the
            usual "Join" button, effectively ignoring the invite link. In particular, the parameter
            :paramref:`creates_join_request` has no effect in this case.
            However, this behavior is undocument and may be subject to change.
            See `this GitHub thread <https://github.com/tdlib/telegram-bot-api/issues/429>`_
            for some discussion.

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            expire_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the link will
                expire. Integer input will be interpreted as Unix timestamp.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            member_limit (:obj:`int`, optional): Maximum number of users that can be members of
                the chat simultaneously after joining the chat via this invite link;
                :tg-const:`telegram.constants.ChatInviteLinkLimit.MIN_MEMBER_LIMIT`-
                :tg-const:`telegram.constants.ChatInviteLinkLimit.MAX_MEMBER_LIMIT`.
            name (:obj:`str`, optional): Invite link name;
                0-:tg-const:`telegram.constants.ChatInviteLinkLimit.NAME_LENGTH` characters.

                .. versionadded:: 13.8
            creates_join_request (:obj:`bool`, optional): :obj:`True`, if users joining the chat
                via the link need to be approved by chat administrators.
                If :obj:`True`, :paramref:`member_limit` can't be specified.

                .. versionadded:: 13.8

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "expire_date": expire_date,
            "member_limit": member_limit,
            "name": name,
            "creates_join_request": creates_join_request,
        }

        result = await self._post(
            "createChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def edit_chat_invite_link(
        self,
        chat_id: Union[str, int],
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
    ) -> ChatInviteLink:
        """
        Use this method to edit a non-primary invite link created by the bot. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.

        Note:
            Though not stated explicitly in the official docs, Telegram changes not only the
            optional parameters that are explicitly passed, but also replaces all other optional
            parameters to the default values. However, since not documented, this behaviour may
            change unbeknown to PTB.

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            invite_link (:obj:`str` | :obj:`telegram.ChatInviteLink`): The invite link to edit.

                .. versionchanged:: 20.0
                    Now also accepts :obj:`telegram.ChatInviteLink` instances.
            expire_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the link will
                expire.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            member_limit (:obj:`int`, optional): Maximum number of users that can be members of
                the chat simultaneously after joining the chat via this invite link;
                :tg-const:`telegram.constants.ChatInviteLinkLimit.MIN_MEMBER_LIMIT`-
                :tg-const:`telegram.constants.ChatInviteLinkLimit.MAX_MEMBER_LIMIT`.
            name (:obj:`str`, optional): Invite link name;
                0-:tg-const:`telegram.constants.ChatInviteLinkLimit.NAME_LENGTH` characters.

                .. versionadded:: 13.8
            creates_join_request (:obj:`bool`, optional): :obj:`True`, if users joining the chat
                via the link need to be approved by chat administrators.
                If :obj:`True`, :paramref:`member_limit` can't be specified.

                .. versionadded:: 13.8

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        link = invite_link.invite_link if isinstance(invite_link, ChatInviteLink) else invite_link
        data: JSONDict = {
            "chat_id": chat_id,
            "invite_link": link,
            "expire_date": expire_date,
            "member_limit": member_limit,
            "name": name,
            "creates_join_request": creates_join_request,
        }

        result = await self._post(
            "editChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def revoke_chat_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: Union[str, "ChatInviteLink"],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> ChatInviteLink:
        """
        Use this method to revoke an invite link created by the bot. If the primary link is
        revoked, a new link is automatically generated. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            invite_link (:obj:`str` | :obj:`telegram.ChatInviteLink`): The invite link to revoke.

                .. versionchanged:: 20.0
                    Now also accepts :obj:`telegram.ChatInviteLink` instances.

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        link = invite_link.invite_link if isinstance(invite_link, ChatInviteLink) else invite_link
        data: JSONDict = {"chat_id": chat_id, "invite_link": link}

        result = await self._post(
            "revokeChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def approve_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to approve a chat join request.

        The bot must be an administrator in the chat for this to work and must have the
        :attr:`telegram.ChatPermissions.can_invite_users` administrator right.

        .. versionadded:: 13.8

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            user_id (:obj:`int`): Unique identifier of the target user.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}

        return await self._post(
            "approveChatJoinRequest",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def decline_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to decline a chat join request.

        The bot must be an administrator in the chat for this to work and must have the
        :attr:`telegram.ChatPermissions.can_invite_users` administrator right.

        .. versionadded:: 13.8

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            user_id (:obj:`int`): Unique identifier of the target user.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}

        return await self._post(
            "declineChatJoinRequest",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_chat_photo(
        self,
        chat_id: Union[str, int],
        photo: FileInput,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to set a new profile photo for the chat.

        Photos can't be changed for private chats. The bot must be an administrator in the chat
        for this to work and must have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            photo (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path`): New chat photo.
                |uploadinput|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "photo": self._parse_file_input(photo)}
        return await self._post(
            "setChatPhoto",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_chat_photo(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to delete a chat photo. Photos can't be changed for private chats. The bot
        must be an administrator in the chat for this to work and must have the appropriate admin
        rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        return await self._post(
            "deleteChatPhoto",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_chat_title(
        self,
        chat_id: Union[str, int],
        title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the title of a chat. Titles can't be changed for private chats.
        The bot must be an administrator in the chat for this to work and must have the appropriate
        admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            title (:obj:`str`): New chat title,
                :tg-const:`telegram.constants.ChatLimit.MIN_CHAT_TITLE_LENGTH`-
                :tg-const:`telegram.constants.ChatLimit.MAX_CHAT_TITLE_LENGTH` characters.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "title": title}
        return await self._post(
            "setChatTitle",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_chat_description(
        self,
        chat_id: Union[str, int],
        description: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the description of a group, a supergroup or a channel. The bot
        must be an administrator in the chat for this to work and must have the appropriate admin
        rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            description (:obj:`str`, optional): New chat description,
                0-:tg-const:`telegram.constants.ChatLimit.CHAT_DESCRIPTION_LENGTH`
                characters.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "description": description}

        return await self._post(
            "setChatDescription",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def pin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to add a message to the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this to work
        and must have the :paramref:`~telegram.ChatAdministratorRights.can_pin_messages` admin
        right in a supergroup or :attr:`~telegram.ChatMemberAdministrator.can_edit_messages` admin
        right in a channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            message_id (:obj:`int`): Identifier of a message to pin.
            disable_notification (:obj:`bool`, optional): Pass :obj:`True`, if it is not necessary
                to send a notification to all chat members about the new pinned message.
                Notifications are always disabled in channels and private chats.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification,
        }

        return await self._post(
            "pinChatMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unpin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to remove a message from the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this to work
        and must have the :paramref:`~telegram.ChatAdministratorRights.can_pin_messages` admin
        right in a supergroup or :attr:`~telegram.ChatMemberAdministrator.can_edit_messages` admin
        right in a channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            message_id (:obj:`int`, optional): Identifier of a message to unpin. If not specified,
                the most recent pinned message (by sending date) will be unpinned.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "message_id": message_id}

        return await self._post(
            "unpinChatMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unpin_all_chat_messages(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to clear the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this
        to work and must have the :paramref:`~telegram.ChatAdministratorRights.can_pin_messages`
        admin right in a supergroup or :attr:`~telegram.ChatMemberAdministrator.can_edit_messages`
        admin right in a channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        return await self._post(
            "unpinAllChatMessages",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_sticker_set(
        self,
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> StickerSet:
        """Use this method to get a sticker set.

        Args:
            name (:obj:`str`): Name of the sticker set.

        Returns:
            :class:`telegram.StickerSet`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"name": name}
        result = await self._post(
            "getStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return StickerSet.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def get_custom_emoji_stickers(
        self,
        custom_emoji_ids: Sequence[str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple[Sticker, ...]:
        # skipcq: FLK-D207
        """
        Use this method to get information about emoji stickers by their identifiers.

        .. versionchanged:: 20.0
            Returns a tuple instead of a list.

        Args:
            custom_emoji_ids (Sequence[:obj:`str`]): Sequence of custom emoji identifiers.
                At most :tg-const:`telegram.constants.CustomEmojiStickerLimit.\
CUSTOM_EMOJI_IDENTIFIER_LIMIT` custom emoji identifiers can be specified.

                .. versionchanged:: 20.0
                    |sequenceargs|

        Returns:
            Tuple[:class:`telegram.Sticker`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"custom_emoji_ids": custom_emoji_ids}
        result = await self._post(
            "getCustomEmojiStickers",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return Sticker.de_list(result, self)

    @_log
    async def upload_sticker_file(
        self,
        user_id: Union[str, int],
        sticker: Optional[FileInput],
        sticker_format: Optional[str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> File:
        """
        Use this method to upload a file with a sticker for later use in the
        :meth:`create_new_sticker_set` and :meth:`add_sticker_to_set` methods (can be used multiple
        times).

        .. versionchanged:: 20.5
           Removed deprecated parameter ``png_sticker``.

        Args:
            user_id (:obj:`int`): User identifier of sticker file owner.
            sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`):
                A file with the sticker in the  ``".WEBP"``, ``".PNG"``, ``".TGS"`` or ``".WEBM"``
                format. See `here <https://core.telegram.org/stickers>`_ for technical requirements
                . |uploadinput|

                .. versionadded:: 20.2

            sticker_format (:obj:`str`): Format of the sticker. Must be one of
                :attr:`telegram.constants.StickerFormat.STATIC`,
                :attr:`telegram.constants.StickerFormat.ANIMATED`,
                :attr:`telegram.constants.StickerFormat.VIDEO`.

                .. versionadded:: 20.2

        Returns:
            :class:`telegram.File`: On success, the uploaded File is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "user_id": user_id,
            "sticker": self._parse_file_input(sticker),  # type: ignore[arg-type]
            "sticker_format": sticker_format,
        }
        result = await self._post(
            "uploadStickerFile",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return File.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def add_sticker_to_set(
        self,
        user_id: Union[str, int],
        name: str,
        sticker: Optional[InputSticker],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to add a new sticker to a set created by the bot. The format of the added
        sticker must match the format of the other stickers in the set. Emoji sticker sets can have
        up to :tg-const:`telegram.constants.StickerSetLimit.MAX_EMOJI_STICKERS` stickers. Animated
        and video sticker sets can have up to
        :tg-const:`telegram.constants.StickerSetLimit.MAX_ANIMATED_STICKERS` stickers. Static
        sticker sets can have up to
        :tg-const:`telegram.constants.StickerSetLimit.MAX_STATIC_STICKERS` stickers.

        .. versionchanged:: 20.2
            Since Bot API 6.6, the parameter :paramref:`sticker` replace the parameters
            ``png_sticker``, ``tgs_sticker``, ``webm_sticker``, ``emojis``, and ``mask_position``.

        .. versionchanged:: 20.5
           Removed deprecated parameters ``png_sticker``, ``tgs_sticker``, ``webm_sticker``,
           ``emojis``, and ``mask_position``.

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.
            name (:obj:`str`): Sticker set name.
            sticker (:class:`telegram.InputSticker`): An object with information about the added
                sticker. If exactly the same sticker had already been added to the set, then the
                set isn't changed.

                .. versionadded:: 20.2

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "user_id": user_id,
            "name": name,
            "sticker": sticker,
        }

        return await self._post(
            "addStickerToSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_sticker_position_in_set(
        self,
        sticker: str,
        position: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to move a sticker in a set created by the bot to a specific position.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            position (:obj:`int`): New sticker position in the set, zero-based.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"sticker": sticker, "position": position}
        return await self._post(
            "setStickerPositionInSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def create_new_sticker_set(
        self,
        user_id: Union[str, int],
        name: str,
        title: str,
        stickers: Optional[Sequence[InputSticker]],
        sticker_format: Optional[str],
        sticker_type: Optional[str] = None,
        needs_repainting: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to create new sticker set owned by a user.
        The bot will be able to edit the created sticker set thus created.

        .. versionchanged:: 20.0
            The parameter ``contains_masks`` has been removed. Use :paramref:`sticker_type`
            instead.

        .. versionchanged:: 20.2
            Since Bot API 6.6, the parameters :paramref:`stickers` and :paramref:`sticker_format`
            replace the parameters ``png_sticker``, ``tgs_sticker``,``webm_sticker``, ``emojis``,
            and ``mask_position``.

        .. versionchanged:: 20.5
            Removed the deprecated parameters mentioned above and adjusted the order of the
            parameters.

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.
            name (:obj:`str`): Short name of sticker set, to be used in t.me/addstickers/ URLs
                (e.g., animals). Can contain only english letters, digits and underscores.
                Must begin with a letter, can't contain consecutive underscores and
                must end in "_by_<bot username>". <bot_username> is case insensitive.
                :tg-const:`telegram.constants.StickerLimit.MIN_NAME_AND_TITLE`-
                :tg-const:`telegram.constants.StickerLimit.MAX_NAME_AND_TITLE` characters.
            title (:obj:`str`): Sticker set title,
                :tg-const:`telegram.constants.StickerLimit.MIN_NAME_AND_TITLE`-
                :tg-const:`telegram.constants.StickerLimit.MAX_NAME_AND_TITLE` characters.

            stickers (Sequence[:class:`telegram.InputSticker`]): A sequence of
                :tg-const:`telegram.constants.StickerSetLimit.MIN_INITIAL_STICKERS`-
                :tg-const:`telegram.constants.StickerSetLimit.MAX_INITIAL_STICKERS` initial
                stickers to be added to the sticker set.

                .. versionadded:: 20.2

            sticker_format (:obj:`str`): Format of stickers in the set, must be one of
                :attr:`~telegram.constants.StickerFormat.STATIC`,
                :attr:`~telegram.constants.StickerFormat.ANIMATED` or
                :attr:`~telegram.constants.StickerFormat.VIDEO`.

                .. versionadded:: 20.2

            sticker_type (:obj:`str`, optional): Type of stickers in the set, pass
                :attr:`telegram.Sticker.REGULAR` or :attr:`telegram.Sticker.MASK`, or
                :attr:`telegram.Sticker.CUSTOM_EMOJI`. By default, a regular sticker set is created

                .. versionadded:: 20.0

            needs_repainting (:obj:`bool`, optional): Pass :obj:`True` if stickers in the sticker
                set must be repainted to the color of text when used in messages, the accent color
                if used as emoji status, white on chat photos, or another appropriate color based
                on context; for custom emoji sticker sets only.

                .. versionadded:: 20.2

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "user_id": user_id,
            "name": name,
            "title": title,
            "stickers": stickers,
            "sticker_format": sticker_format,
            "sticker_type": sticker_type,
            "needs_repainting": needs_repainting,
        }

        return await self._post(
            "createNewStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_sticker_from_set(
        self,
        sticker: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to delete a sticker from a set created by the bot.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"sticker": sticker}
        return await self._post(
            "deleteStickerFromSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_sticker_set(
        self,
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to delete a sticker set that was created by the bot.

        .. versionadded:: 20.2

        Args:
            name (:obj:`str`): Sticker set name.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"name": name}
        return await self._post(
            "deleteStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_sticker_set_thumbnail(
        self,
        name: str,
        user_id: Union[str, int],
        thumbnail: Optional[FileInput] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to set the thumbnail of a regular or mask sticker set. The format of the
        thumbnail file must match the format of the stickers in the set.

        .. versionadded:: 20.2

        Args:
            name (:obj:`str`): Sticker set name
            user_id (:obj:`int`): User identifier of created sticker set owner.
            thumbnail (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): A **.WEBP** or **.PNG** image with the thumbnail, must
                be up to :tg-const:`telegram.constants.StickerSetLimit.MAX_STATIC_THUMBNAIL_SIZE`
                kilobytes in size and have width and height of exactly
                :tg-const:`telegram.constants.StickerSetLimit.STATIC_THUMB_DIMENSIONS` px, or a
                **.TGS** animation with the thumbnail up to
                :tg-const:`telegram.constants.StickerSetLimit.MAX_ANIMATED_THUMBNAIL_SIZE`
                kilobytes in size; see
                `the docs <https://core.telegram.org/stickers#animation-requirements>`_ for
                animated sticker technical requirements, or a **.WEBM** video with the thumbnail up
                to :tg-const:`telegram.constants.StickerSetLimit.MAX_ANIMATED_THUMBNAIL_SIZE`
                kilobytes in size; see
                `this <https://core.telegram.org/stickers#video-requirements>`_ for video sticker
                technical requirements.

                |fileinput|

                Animated and video sticker set thumbnails can't be uploaded via HTTP URL. If
                omitted, then the thumbnail is dropped and the first sticker is used as the
                thumbnail.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "name": name,
            "user_id": user_id,
            "thumbnail": self._parse_file_input(thumbnail) if thumbnail else None,
        }

        return await self._post(
            "setStickerSetThumbnail",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_sticker_set_title(
        self,
        name: str,
        title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to set the title of a created sticker set.

        .. versionadded:: 20.2

        Args:
            name (:obj:`str`): Sticker set name.
            title (:obj:`str`): Sticker set title,
                :tg-const:`telegram.constants.StickerLimit.MIN_NAME_AND_TITLE`-
                :tg-const:`telegram.constants.StickerLimit.MAX_NAME_AND_TITLE` characters.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"name": name, "title": title}
        return await self._post(
            "setStickerSetTitle",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_sticker_emoji_list(
        self,
        sticker: str,
        emoji_list: Sequence[str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the list of emoji assigned to a regular or custom emoji sticker.
        The sticker must belong to a sticker set created by the bot.

        .. versionadded:: 20.2

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            emoji_list (Sequence[:obj:`str`]): A sequence of
                :tg-const:`telegram.constants.StickerLimit.MIN_STICKER_EMOJI`-
                :tg-const:`telegram.constants.StickerLimit.MAX_STICKER_EMOJI` emoji associated with
                the sticker.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"sticker": sticker, "emoji_list": emoji_list}
        return await self._post(
            "setStickerEmojiList",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_sticker_keywords(
        self,
        sticker: str,
        keywords: Optional[Sequence[str]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change search keywords assigned to a regular or custom emoji sticker.
        The sticker must belong to a sticker set created by the bot.

        .. versionadded:: 20.2

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            keywords (Sequence[:obj:`str`]): A sequence of
                0-:tg-const:`telegram.constants.StickerLimit.MAX_SEARCH_KEYWORDS` search keywords
                for the sticker with total length up to
                :tg-const:`telegram.constants.StickerLimit.MAX_KEYWORD_LENGTH` characters.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"sticker": sticker, "keywords": keywords}
        return await self._post(
            "setStickerKeywords",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_sticker_mask_position(
        self,
        sticker: str,
        mask_position: Optional[MaskPosition] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the mask position of a mask sticker.
        The sticker must belong to a sticker set that was created by the bot.

        .. versionadded:: 20.2

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            mask_position (:class:`telegram.MaskPosition`, optional): A object with the position
                where the mask should be placed on faces. Omit the parameter to remove the mask
                position.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"sticker": sticker, "mask_position": mask_position}
        return await self._post(
            "setStickerMaskPosition",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_custom_emoji_sticker_set_thumbnail(
        self,
        name: str,
        custom_emoji_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to set the thumbnail of a custom emoji sticker set.

        .. versionadded:: 20.2

        Args:
            name (:obj:`str`): Sticker set name.
            custom_emoji_id (:obj:`str`, optional): Custom emoji identifier of a sticker from the
                sticker set; pass an empty string to drop the thumbnail and use the first sticker
                as the thumbnail.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"name": name, "custom_emoji_id": custom_emoji_id}

        return await self._post(
            "setCustomEmojiStickerSetThumbnail",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_passport_data_errors(
        self,
        user_id: Union[str, int],
        errors: Sequence[PassportElementError],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Informs a user that some of the Telegram Passport elements they provided contains errors.
        The user will not be able to re-submit their Passport to you until the errors are fixed
        (the contents of the field for which you returned the error must change).

        Use this if the data submitted by the user doesn't satisfy the standards your service
        requires for any reason. For example, if a birthday date seems invalid, a submitted
        document is blurry, a scan shows evidence of tampering, etc. Supply some details in the
        error message to make sure the user knows how to correct the issues.

        Args:
            user_id (:obj:`int`): User identifier
            errors (Sequence[:class:`PassportElementError`]): A Sequence describing the errors.

                .. versionchanged:: 20.0
                    |sequenceargs|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id, "errors": errors}
        return await self._post(
            "setPassportDataErrors",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_poll(
        self,
        chat_id: Union[int, str],
        question: str,
        options: Sequence[str],
        is_anonymous: Optional[bool] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
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
    ) -> Message:
        """
        Use this method to send a native poll.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            question (:obj:`str`): Poll question, :tg-const:`telegram.Poll.MIN_QUESTION_LENGTH`-
                :tg-const:`telegram.Poll.MAX_QUESTION_LENGTH` characters.
            options (Sequence[:obj:`str`]): Sequence of answer options,
                :tg-const:`telegram.Poll.MIN_OPTION_NUMBER`-
                :tg-const:`telegram.Poll.MAX_OPTION_NUMBER` strings
                :tg-const:`telegram.Poll.MIN_OPTION_LENGTH`-
                :tg-const:`telegram.Poll.MAX_OPTION_LENGTH` characters each.

                .. versionchanged:: 20.0
                    |sequenceargs|
            is_anonymous (:obj:`bool`, optional): :obj:`True`, if the poll needs to be anonymous,
                defaults to :obj:`True`.
            type (:obj:`str`, optional): Poll type, :tg-const:`telegram.Poll.QUIZ` or
                :tg-const:`telegram.Poll.REGULAR`, defaults to :tg-const:`telegram.Poll.REGULAR`.
            allows_multiple_answers (:obj:`bool`, optional): :obj:`True`, if the poll allows
                multiple answers, ignored for polls in quiz mode, defaults to :obj:`False`.
            correct_option_id (:obj:`int`, optional): 0-based identifier of the correct answer
                option, required for polls in quiz mode.
            explanation (:obj:`str`, optional): Text that is shown when a user chooses an incorrect
                answer or taps on the lamp icon in a quiz-style poll,
                0-:tg-const:`telegram.Poll.MAX_EXPLANATION_LENGTH` characters with at most
                :tg-const:`telegram.Poll.MAX_EXPLANATION_LINE_FEEDS` line feeds after entities
                parsing.
            explanation_parse_mode (:obj:`str`, optional): Mode for parsing entities in the
                explanation. See the constants in :class:`telegram.constants.ParseMode` for the
                available modes.
            explanation_entities (Sequence[:class:`telegram.MessageEntity`], optional): Sequence of
                special entities that appear in message text, which can be specified instead of
                :paramref:`explanation_parse_mode`.

                .. versionchanged:: 20.0
                    |sequenceargs|
            open_period (:obj:`int`, optional): Amount of time in seconds the poll will be active
                after creation, :tg-const:`telegram.Poll.MIN_OPEN_PERIOD`-
                :tg-const:`telegram.Poll.MAX_OPEN_PERIOD`. Can't be used together with
                :paramref:`close_date`.
            close_date (:obj:`int` | :obj:`datetime.datetime`, optional): Point in time (Unix
                timestamp) when the poll will be automatically closed. Must be at least
                :tg-const:`telegram.Poll.MIN_OPEN_PERIOD` and no more than
                :tg-const:`telegram.Poll.MAX_OPEN_PERIOD` seconds in the future.
                Can't be used together with :paramref:`open_period`.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            is_closed (:obj:`bool`, optional): Pass :obj:`True`, if the poll needs to be
                immediately closed. This can be useful for poll preview.
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "explanation_parse_mode": explanation_parse_mode,
            "is_anonymous": is_anonymous,
            "type": type,
            "allows_multiple_answers": allows_multiple_answers,
            "correct_option_id": correct_option_id,
            "is_closed": is_closed,
            "explanation": explanation,
            "explanation_entities": explanation_entities,
            "open_period": open_period,
            "close_date": close_date,
        }

        return await self._send_message(
            "sendPoll",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def stop_poll(
        self,
        chat_id: Union[int, str],
        message_id: int,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Poll:
        """
        Use this method to stop a poll which was sent by the bot.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            message_id (:obj:`int`): Identifier of the original message with the poll.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                message inline keyboard.

        Returns:
            :class:`telegram.Poll`: On success, the stopped Poll is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": reply_markup,
        }

        result = await self._post(
            "stopPoll",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return Poll.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def send_dice(
        self,
        chat_id: Union[int, str],
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
    ) -> Message:
        """
        Use this method to send an animated emoji that will display a random value.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            disable_notification (:obj:`bool`, optional): |disable_notification|
            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user
            emoji (:obj:`str`, optional): Emoji on which the dice throw animation is based.
                Currently, must be one of :class:`telegram.constants.DiceEmoji`. Dice can have
                values
                :tg-const:`telegram.Dice.MIN_VALUE`-:tg-const:`telegram.Dice.MAX_VALUE_BOWLING`
                for :tg-const:`telegram.Dice.DICE`, :tg-const:`telegram.Dice.DARTS` and
                :tg-const:`telegram.Dice.BOWLING`, values
                :tg-const:`telegram.Dice.MIN_VALUE`-:tg-const:`telegram.Dice.MAX_VALUE_BASKETBALL`
                for :tg-const:`telegram.Dice.BASKETBALL` and :tg-const:`telegram.Dice.FOOTBALL`,
                and values :tg-const:`telegram.Dice.MIN_VALUE`-
                :tg-const:`telegram.Dice.MAX_VALUE_SLOT_MACHINE`
                for :tg-const:`telegram.Dice.SLOT_MACHINE`. Defaults to
                :tg-const:`telegram.Dice.DICE`.

                .. versionchanged:: 13.4
                   Added the :tg-const:`telegram.Dice.BOWLING` emoji.
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "emoji": emoji}

        return await self._send_message(
            "sendDice",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_my_default_administrator_rights(
        self,
        for_channels: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> ChatAdministratorRights:
        """Use this method to get the current default administrator rights of the bot.

        .. seealso:: :meth:`set_my_default_administrator_rights`

        .. versionadded:: 20.0

        Args:
            for_channels (:obj:`bool`, optional): Pass :obj:`True` to get default administrator
                rights of the bot in channels. Otherwise, default administrator rights of the bot
                for groups and supergroups will be returned.

        Returns:
            :class:`telegram.ChatAdministratorRights`: On success.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"for_channels": for_channels}

        result = await self._post(
            "getMyDefaultAdministratorRights",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatAdministratorRights.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def set_my_default_administrator_rights(
        self,
        rights: Optional[ChatAdministratorRights] = None,
        for_channels: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to change the default administrator rights requested by the bot when
        it's added as an administrator to groups or channels. These rights will be suggested to
        users, but they are are free to modify the list before adding the bot.

        .. seealso:: :meth:`get_my_default_administrator_rights`

        .. versionadded:: 20.0

        Args:
            rights (:obj:`telegram.ChatAdministratorRights`, optional): A
                :obj:`telegram.ChatAdministratorRights` object describing new default administrator
                rights. If not specified, the default administrator rights will be cleared.
            for_channels (:obj:`bool`, optional): Pass :obj:`True` to change the default
                administrator rights of the bot in channels. Otherwise, the default administrator
                rights of the bot for groups and supergroups will be changed.

        Returns:
            :obj:`bool`: Returns :obj:`True` on success.

        Raises:
            :obj:`telegram.error.TelegramError`
        """
        data: JSONDict = {"rights": rights, "for_channels": for_channels}

        return await self._post(
            "setMyDefaultAdministratorRights",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_my_commands(
        self,
        scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple[BotCommand, ...]:
        """
        Use this method to get the current list of the bot's commands for the given scope and user
        language.

        .. seealso:: :meth:`set_my_commands`, :meth:`delete_my_commands`

        .. versionchanged:: 20.0
            Returns a tuple instead of a list.

        Args:
            scope (:class:`telegram.BotCommandScope`, optional): An object,
                describing scope of users. Defaults to :class:`telegram.BotCommandScopeDefault`.

                .. versionadded:: 13.7

            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code or an empty
                string.

                .. versionadded:: 13.7

        Returns:
            Tuple[:class:`telegram.BotCommand`]: On success, the commands set for the bot. An empty
            tuple is returned if commands are not set.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"scope": scope, "language_code": language_code}

        result = await self._post(
            "getMyCommands",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return BotCommand.de_list(result, self)

    @_log
    async def set_my_commands(
        self,
        commands: Sequence[Union[BotCommand, Tuple[str, str]]],
        scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the list of the bot's commands. See the
        `Telegram docs <https://core.telegram.org/bots/features#commands>`_ for more details about
        bot commands.

        .. seealso:: :meth:`get_my_commands`, :meth:`delete_my_commands`

        Args:
            commands (Sequence[:class:`BotCommand` | (:obj:`str`, :obj:`str`)]): A sequence
                of bot commands to be set as the list of the bot's commands. At most
                :tg-const:`telegram.constants.BotCommandLimit.MAX_COMMAND_NUMBER` commands can be
                specified.

                Note:
                    If you pass in a sequence of :obj:`tuple`, the order of elements in each
                    :obj:`tuple` must correspond to the order of positional arguments to create a
                    :class:`BotCommand` instance.

                .. versionchanged:: 20.0
                    |sequenceargs|
            scope (:class:`telegram.BotCommandScope`, optional): An object,
                describing scope of users for which the commands are relevant. Defaults to
                :class:`telegram.BotCommandScopeDefault`.

                .. versionadded:: 13.7

            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                commands will be applied to all users from the given scope, for whose language
                there are no dedicated commands.

                .. versionadded:: 13.7

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        cmds = [c if isinstance(c, BotCommand) else BotCommand(c[0], c[1]) for c in commands]
        data: JSONDict = {"commands": cmds, "scope": scope, "language_code": language_code}

        return await self._post(
            "setMyCommands",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_my_commands(
        self,
        scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to delete the list of the bot's commands for the given scope and user
        language. After deletion,
        `higher level commands <https://core.telegram.org/bots/api#determining-list-of-commands>`_
        will be shown to affected users.

        .. versionadded:: 13.7

        .. seealso:: :meth:`get_my_commands`, :meth:`set_my_commands`

        Args:
            scope (:class:`telegram.BotCommandScope`, optional): An object,
                describing scope of users for which the commands are relevant. Defaults to
                :class:`telegram.BotCommandScopeDefault`.
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                commands will be applied to all users from the given scope, for whose language
                there are no dedicated commands.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"scope": scope, "language_code": language_code}

        return await self._post(
            "deleteMyCommands",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def log_out(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to log out from the cloud Bot API server before launching the bot locally.
        You *must* log out the bot before running it locally, otherwise there is no guarantee that
        the bot will receive updates. After a successful call, you can immediately log in on a
        local server, but will not be able to log in back to the cloud Bot API server for 10
        minutes.

        Returns:
            :obj:`True`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return await self._post(
            "logOut",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def close(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to close the bot instance before moving it from one local server to
        another. You need to delete the webhook before calling this method to ensure that the bot
        isn't launched again after server restart. The method will return error 429 in the first
        10 minutes after the bot is launched.

        Returns:
            :obj:`True`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return await self._post(
            "close",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def copy_message(
        self,
        chat_id: Union[int, str],
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
    ) -> MessageId:
        """
        Use this method to copy messages of any kind. Service messages and invoice messages can't
        be copied. The method is analogous to the method :meth:`forward_message`, but the copied
        message doesn't have a link to the original message.

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|
            from_chat_id (:obj:`int` | :obj:`str`): Unique identifier for the chat where the
                original message was sent (or channel username in the format ``@channelusername``).
            message_id (:obj:`int`): Message identifier in the chat specified in from_chat_id.
            caption (:obj:`str`, optional): New caption for media,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing. If not specified, the original caption is kept.
            parse_mode (:obj:`str`, optional): Mode for parsing entities in the new caption. See
                the constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
                |caption_entities|

                .. versionchanged:: 20.0
                    |sequenceargs|
            disable_notification (:obj:`bool`, optional): |disable_notification|
            protect_content (:obj:`bool`, optional): |protect_content|

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 20.0

            reply_to_message_id (:obj:`int`, optional): |reply_to_msg_id|
            allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply|
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :class:`telegram.MessageId`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
            "allow_sending_without_reply": allow_sending_without_reply,
            "protect_content": protect_content,
            "caption": caption,
            "caption_entities": caption_entities,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
            "message_thread_id": message_thread_id,
        }

        result = await self._post(
            "copyMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return MessageId.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def set_chat_menu_button(
        self,
        chat_id: Optional[int] = None,
        menu_button: Optional[MenuButton] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Use this method to change the bot's menu button in a private chat, or the default menu
        button.

        .. seealso:: :meth:`get_chat_menu_button`, :meth:`telegram.Chat.get_menu_button`
            :meth:`telegram.User.get_menu_button`

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int`, optional): Unique identifier for the target private chat. If not
                specified, default bot's menu button will be changed
            menu_button (:class:`telegram.MenuButton`, optional): An object for the new bot's menu
                button. Defaults to :class:`telegram.MenuButtonDefault`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        data: JSONDict = {"chat_id": chat_id, "menu_button": menu_button}

        return await self._post(
            "setChatMenuButton",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_chat_menu_button(
        self,
        chat_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> MenuButton:
        """Use this method to get the current value of the bot's menu button in a private chat, or
        the default menu button.

        .. seealso:: :meth:`set_chat_menu_button`, :meth:`telegram.Chat.set_menu_button`,
            :meth:`telegram.User.set_menu_button`

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int`, optional): Unique identifier for the target private chat. If not
                specified, default bot's menu button will be returned.

        Returns:
            :class:`telegram.MenuButton`: On success, the current menu button is returned.

        """
        data = {"chat_id": chat_id}

        result = await self._post(
            "getChatMenuButton",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return MenuButton.de_json(result, bot=self)  # type: ignore[return-value]

    @_log
    async def create_invoice_link(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: Sequence["LabeledPrice"],
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[Sequence[int]] = None,
        provider_data: Optional[Union[str, object]] = None,
        photo_url: Optional[str] = None,
        photo_size: Optional[int] = None,
        photo_width: Optional[int] = None,
        photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> str:
        """Use this method to create a link for an invoice.

        .. versionadded:: 20.0

        Args:
            title (:obj:`str`): Product name. :tg-const:`telegram.Invoice.MIN_TITLE_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_TITLE_LENGTH` characters.
            description (:obj:`str`): Product description.
                :tg-const:`telegram.Invoice.MIN_DESCRIPTION_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_DESCRIPTION_LENGTH` characters.
            payload (:obj:`str`): Bot-defined invoice payload.
                :tg-const:`telegram.Invoice.MIN_PAYLOAD_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_PAYLOAD_LENGTH` bytes. This will not be
                displayed to the user, use for your internal processes.
            provider_token (:obj:`str`): Payments provider token, obtained via
                `@BotFather <https://t.me/BotFather>`_.
            currency (:obj:`str`): Three-letter ISO 4217 currency code, see `more on currencies
                <https://core.telegram.org/bots/payments#supported-currencies>`_.
            prices (Sequence[:class:`telegram.LabeledPrice`)]: Price breakdown, a sequence
                of components (e.g. product price, tax, discount, delivery cost, delivery tax,
                bonus, etc.).

                .. versionchanged:: 20.0
                    |sequenceargs|
            max_tip_amount (:obj:`int`, optional): The maximum accepted amount for tips in the
                *smallest* units of the currency (integer, **not** float/double). For example, for
                a maximum tip of US$ 1.45 pass ``max_tip_amount = 145``. See the exp parameter in
                `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it
                shows the number of digits past the decimal point for each currency (2 for the
                majority of currencies). Defaults to ``0``.
            suggested_tip_amounts (Sequence[:obj:`int`], optional): An array of
                suggested amounts of tips in the *smallest* units of the currency (integer, **not**
                float/double). At most :tg-const:`telegram.Invoice.MAX_TIP_AMOUNTS` suggested tip
                amounts can be specified. The suggested tip amounts must be positive, passed in a
                strictly increased order and must not exceed :paramref:`max_tip_amount`.

                .. versionchanged:: 20.0
                    |sequenceargs|
            provider_data (:obj:`str` | :obj:`object`, optional): Data about the
                invoice, which will be shared with the payment provider. A detailed description of
                required fields should be provided by the payment provider. When an object is
                passed, it will be encoded as JSON.
            photo_url (:obj:`str`, optional): URL of the product photo for the invoice. Can be a
                photo of the goods or a marketing image for a service.
            photo_size (:obj:`int`, optional): Photo size in bytes.
            photo_width (:obj:`int`, optional): Photo width.
            photo_height (:obj:`int`, optional): Photo height.
            need_name (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's full
                name to complete the order.
            need_phone_number (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's
                phone number to complete the order.
            need_email (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's email
                address to complete the order.
            need_shipping_address (:obj:`bool`, optional): Pass :obj:`True`, if you require the
                user's shipping address to complete the order.
            send_phone_number_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's
                phone number should be sent to provider.
            send_email_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's email
                address should be sent to provider.
            is_flexible (:obj:`bool`, optional): Pass :obj:`True`, if the final price depends on
                the shipping method.

        Returns:
            :class:`str`: On success, the created invoice link is returned.

        """
        data: JSONDict = {
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": currency,
            "prices": prices,
            "max_tip_amount": max_tip_amount,
            "suggested_tip_amounts": suggested_tip_amounts,
            "provider_data": provider_data,
            "photo_url": photo_url,
            "photo_size": photo_size,
            "photo_width": photo_width,
            "photo_height": photo_height,
            "need_name": need_name,
            "need_phone_number": need_phone_number,
            "need_email": need_email,
            "need_shipping_address": need_shipping_address,
            "is_flexible": is_flexible,
            "send_phone_number_to_provider": send_phone_number_to_provider,
            "send_email_to_provider": send_email_to_provider,
        }

        return await self._post(
            "createInvoiceLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_forum_topic_icon_stickers(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Tuple[Sticker, ...]:
        """Use this method to get custom emoji stickers, which can be used as a forum topic
        icon by any user. Requires no parameters.

        .. versionadded:: 20.0

        Returns:
            Tuple[:class:`telegram.Sticker`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        result = await self._post(
            "getForumTopicIconStickers",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return Sticker.de_list(result, self)

    @_log
    async def create_forum_topic(
        self,
        chat_id: Union[str, int],
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
        """
        Use this method to create a topic in a forum supergroup chat. The bot must be
        an administrator in the chat for this to work and must have
        :paramref:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            name (:obj:`str`): New topic name,
                :tg-const:`telegram.constants.ForumTopicLimit.MIN_NAME_LENGTH`-
                :tg-const:`telegram.constants.ForumTopicLimit.MAX_NAME_LENGTH` characters.
            icon_color (:obj:`int`, optional): Color of the topic icon in RGB format. Currently,
                must be one of :attr:`telegram.constants.ForumIconColor.BLUE`,
                :attr:`telegram.constants.ForumIconColor.YELLOW`,
                :attr:`telegram.constants.ForumIconColor.PURPLE`,
                :attr:`telegram.constants.ForumIconColor.GREEN`,
                :attr:`telegram.constants.ForumIconColor.PINK`, or
                :attr:`telegram.constants.ForumIconColor.RED`.
            icon_custom_emoji_id (:obj:`str`, optional): New unique identifier of the custom emoji
                shown as the topic icon. Use :meth:`~telegram.Bot.get_forum_topic_icon_stickers`
                to get all allowed custom emoji identifiers.

        Returns:
            :class:`telegram.ForumTopic`

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "name": name,
            "icon_color": icon_color,
            "icon_custom_emoji_id": icon_custom_emoji_id,
        }
        result = await self._post(
            "createForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return ForumTopic.de_json(result, self)  # type: ignore[return-value]

    @_log
    async def edit_forum_topic(
        self,
        chat_id: Union[str, int],
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
        """
        Use this method to edit name and icon of a topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :paramref:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights,
        unless it is the creator of the topic.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|
            name (:obj:`str`, optional): New topic name,
                :tg-const:`telegram.constants.ForumTopicLimit.MIN_NAME_LENGTH`-
                :tg-const:`telegram.constants.ForumTopicLimit.MAX_NAME_LENGTH` characters. If
                not specified or empty, the current name of the topic will be kept.
            icon_custom_emoji_id (:obj:`str`, optional): New unique identifier of the custom emoji
                shown as the topic icon. Use :meth:`~telegram.Bot.get_forum_topic_icon_stickers`
                to get all allowed custom emoji identifiers.Pass an empty string to remove the
                icon. If not specified, the current icon will be kept.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
            "name": name,
            "icon_custom_emoji_id": icon_custom_emoji_id,
        }
        return await self._post(
            "editForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def close_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to close an open topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :paramref:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights,
        unless it is the creator of the topic.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return await self._post(
            "closeForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def reopen_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to reopen a closed topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :paramref:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights,
        unless it is the creator of the topic.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return await self._post(
            "reopenForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to delete a forum topic along with all its messages in a forum supergroup
        chat. The bot must be an administrator in the chat for this to work and must have
        :paramref:`~telegram.ChatAdministratorRights.can_delete_messages` administrator rights.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return await self._post(
            "deleteForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unpin_all_forum_topic_messages(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to clear the list of pinned messages in a forum topic. The bot must
        be an administrator in the chat for this to work and must have
        :paramref:`~telegram.ChatAdministratorRights.can_pin_messages` administrator rights
        in the supergroup.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return await self._post(
            "unpinAllForumTopicMessages",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unpin_all_general_forum_topic_messages(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to clear the list of pinned messages in a General forum topic. The bot must
        be an administrator in the chat for this to work and must have
        :paramref:`~telegram.ChatAdministratorRights.can_pin_messages` administrator rights in the
        supergroup.

        .. versionadded:: 20.5

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"chat_id": chat_id}

        return await self._post(
            "unpinAllGeneralForumTopicMessages",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_general_forum_topic(
        self,
        chat_id: Union[str, int],
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to edit the name of the 'General' topic in a forum supergroup chat. The bot
        must be an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            name (:obj:`str`): New topic name,
                :tg-const:`telegram.constants.ForumTopicLimit.MIN_NAME_LENGTH`-
                :tg-const:`telegram.constants.ForumTopicLimit.MAX_NAME_LENGTH` characters.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "name": name}

        return await self._post(
            "editGeneralForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def close_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to close an open 'General' topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        return await self._post(
            "closeGeneralForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def reopen_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to reopen a closed 'General' topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights.
        The topic will be automatically unhidden if it was hidden.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        return await self._post(
            "reopenGeneralForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def hide_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to hide the 'General' topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights.
        The topic will be automatically closed if it was open.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        return await self._post(
            "hideGeneralForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unhide_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to unhide the 'General' topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights.

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        return await self._post(
            "unhideGeneralForumTopic",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_my_description(
        self,
        description: Optional[str] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the bot's description, which is shown in the chat with the bot
        if the chat is empty.

        .. versionadded:: 20.2

        Args:
            description (:obj:`str`, optional): New bot description;
                0-:tg-const:`telegram.constants.BotDescriptionLimit.MAX_DESCRIPTION_LENGTH`
                characters. Pass an empty string to remove the dedicated description for the given
                language.
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                the description will be applied to all users for whose language there is no
                dedicated description.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"description": description, "language_code": language_code}

        return await self._post(
            "setMyDescription",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def set_my_short_description(
        self,
        short_description: Optional[str] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the bot's short description, which is shown on the bot's profile
        page and is sent together with the link when users share the bot.

        .. versionadded:: 20.2

        Args:
            short_description (:obj:`str`, optional): New short description for the bot;
                0-:tg-const:`telegram.constants.BotDescriptionLimit.MAX_SHORT_DESCRIPTION_LENGTH`
                characters. Pass an empty string to remove the dedicated description for the given
                language.
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                the description will be applied to all users for whose language there is no
                dedicated description.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"short_description": short_description, "language_code": language_code}

        return await self._post(
            "setMyShortDescription",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_my_description(
        self,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> BotDescription:
        """
        Use this method to get the current bot description for the given user language.

        Args:
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code or an empty
                string.

        Returns:
            :class:`telegram.BotDescription`: On success, the bot description is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data = {"language_code": language_code}
        return BotDescription.de_json(  # type: ignore[return-value]
            await self._post(
                "getMyDescription",
                data,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
            ),
            bot=self,
        )

    @_log
    async def get_my_short_description(
        self,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> BotShortDescription:
        """
        Use this method to get the current bot short description for the given user language.

        Args:
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code or an empty
                string.

        Returns:
            :class:`telegram.BotShortDescription`: On success, the bot short description is
                returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data = {"language_code": language_code}
        return BotShortDescription.de_json(  # type: ignore[return-value]
            await self._post(
                "getMyShortDescription",
                data,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
            ),
            bot=self,
        )

    @_log
    async def set_my_name(
        self,
        name: Optional[str] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Use this method to change the bot's name.

        .. versionadded:: 20.3

        Args:
            name (:obj:`str`, optional): New bot name;
                0-:tg-const:`telegram.constants.BotNameLimit.MAX_NAME_LENGTH`
                characters. Pass an empty string to remove the dedicated name for the given
                language.

                Caution:
                    If :paramref:`language_code` is not specified, a :paramref:`name` *must*
                    be specified.
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                the name will be applied to all users for whose language there is no
                dedicated name.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"name": name, "language_code": language_code}

        return await self._post(
            "setMyName",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_my_name(
        self,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> BotName:
        """
        Use this method to get the current bot name for the given user language.

        Args:
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code or an empty
                string.

        Returns:
            :class:`telegram.BotName`: On success, the bot name is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data = {"language_code": language_code}
        return BotName.de_json(  # type: ignore[return-value]
            await self._post(
                "getMyName",
                data,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
            ),
            bot=self,
        )

    def to_dict(self, recursive: bool = True) -> JSONDict:  # skipcq: PYL-W0613
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data: JSONDict = {"id": self.id, "username": self.username, "first_name": self.first_name}

        if self.last_name:
            data["last_name"] = self.last_name

        return data

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.bot == other.bot
        return False

    def __hash__(self) -> int:
        return hash((self.__class__, self.bot))

    # camelCase aliases
    getMe = get_me
    """Alias for :meth:`get_me`"""
    sendMessage = send_message
    """Alias for :meth:`send_message`"""
    deleteMessage = delete_message
    """Alias for :meth:`delete_message`"""
    forwardMessage = forward_message
    """Alias for :meth:`forward_message`"""
    sendPhoto = send_photo
    """Alias for :meth:`send_photo`"""
    sendAudio = send_audio
    """Alias for :meth:`send_audio`"""
    sendDocument = send_document
    """Alias for :meth:`send_document`"""
    sendSticker = send_sticker
    """Alias for :meth:`send_sticker`"""
    sendVideo = send_video
    """Alias for :meth:`send_video`"""
    sendAnimation = send_animation
    """Alias for :meth:`send_animation`"""
    sendVoice = send_voice
    """Alias for :meth:`send_voice`"""
    sendVideoNote = send_video_note
    """Alias for :meth:`send_video_note`"""
    sendMediaGroup = send_media_group
    """Alias for :meth:`send_media_group`"""
    sendLocation = send_location
    """Alias for :meth:`send_location`"""
    editMessageLiveLocation = edit_message_live_location
    """Alias for :meth:`edit_message_live_location`"""
    stopMessageLiveLocation = stop_message_live_location
    """Alias for :meth:`stop_message_live_location`"""
    sendVenue = send_venue
    """Alias for :meth:`send_venue`"""
    sendContact = send_contact
    """Alias for :meth:`send_contact`"""
    sendGame = send_game
    """Alias for :meth:`send_game`"""
    sendChatAction = send_chat_action
    """Alias for :meth:`send_chat_action`"""
    answerInlineQuery = answer_inline_query
    """Alias for :meth:`answer_inline_query`"""
    getUserProfilePhotos = get_user_profile_photos
    """Alias for :meth:`get_user_profile_photos`"""
    getFile = get_file
    """Alias for :meth:`get_file`"""
    banChatMember = ban_chat_member
    """Alias for :meth:`ban_chat_member`"""
    banChatSenderChat = ban_chat_sender_chat
    """Alias for :meth:`ban_chat_sender_chat`"""
    unbanChatMember = unban_chat_member
    """Alias for :meth:`unban_chat_member`"""
    unbanChatSenderChat = unban_chat_sender_chat
    """Alias for :meth:`unban_chat_sender_chat`"""
    answerCallbackQuery = answer_callback_query
    """Alias for :meth:`answer_callback_query`"""
    editMessageText = edit_message_text
    """Alias for :meth:`edit_message_text`"""
    editMessageCaption = edit_message_caption
    """Alias for :meth:`edit_message_caption`"""
    editMessageMedia = edit_message_media
    """Alias for :meth:`edit_message_media`"""
    editMessageReplyMarkup = edit_message_reply_markup
    """Alias for :meth:`edit_message_reply_markup`"""
    getUpdates = get_updates
    """Alias for :meth:`get_updates`"""
    setWebhook = set_webhook
    """Alias for :meth:`set_webhook`"""
    deleteWebhook = delete_webhook
    """Alias for :meth:`delete_webhook`"""
    leaveChat = leave_chat
    """Alias for :meth:`leave_chat`"""
    getChat = get_chat
    """Alias for :meth:`get_chat`"""
    getChatAdministrators = get_chat_administrators
    """Alias for :meth:`get_chat_administrators`"""
    getChatMember = get_chat_member
    """Alias for :meth:`get_chat_member`"""
    setChatStickerSet = set_chat_sticker_set
    """Alias for :meth:`set_chat_sticker_set`"""
    deleteChatStickerSet = delete_chat_sticker_set
    """Alias for :meth:`delete_chat_sticker_set`"""
    getChatMemberCount = get_chat_member_count
    """Alias for :meth:`get_chat_member_count`"""
    getWebhookInfo = get_webhook_info
    """Alias for :meth:`get_webhook_info`"""
    setGameScore = set_game_score
    """Alias for :meth:`set_game_score`"""
    getGameHighScores = get_game_high_scores
    """Alias for :meth:`get_game_high_scores`"""
    sendInvoice = send_invoice
    """Alias for :meth:`send_invoice`"""
    answerShippingQuery = answer_shipping_query
    """Alias for :meth:`answer_shipping_query`"""
    answerPreCheckoutQuery = answer_pre_checkout_query
    """Alias for :meth:`answer_pre_checkout_query`"""
    answerWebAppQuery = answer_web_app_query
    """Alias for :meth:`answer_web_app_query`"""
    restrictChatMember = restrict_chat_member
    """Alias for :meth:`restrict_chat_member`"""
    promoteChatMember = promote_chat_member
    """Alias for :meth:`promote_chat_member`"""
    setChatPermissions = set_chat_permissions
    """Alias for :meth:`set_chat_permissions`"""
    setChatAdministratorCustomTitle = set_chat_administrator_custom_title
    """Alias for :meth:`set_chat_administrator_custom_title`"""
    exportChatInviteLink = export_chat_invite_link
    """Alias for :meth:`export_chat_invite_link`"""
    createChatInviteLink = create_chat_invite_link
    """Alias for :meth:`create_chat_invite_link`"""
    editChatInviteLink = edit_chat_invite_link
    """Alias for :meth:`edit_chat_invite_link`"""
    revokeChatInviteLink = revoke_chat_invite_link
    """Alias for :meth:`revoke_chat_invite_link`"""
    approveChatJoinRequest = approve_chat_join_request
    """Alias for :meth:`approve_chat_join_request`"""
    declineChatJoinRequest = decline_chat_join_request
    """Alias for :meth:`decline_chat_join_request`"""
    setChatPhoto = set_chat_photo
    """Alias for :meth:`set_chat_photo`"""
    deleteChatPhoto = delete_chat_photo
    """Alias for :meth:`delete_chat_photo`"""
    setChatTitle = set_chat_title
    """Alias for :meth:`set_chat_title`"""
    setChatDescription = set_chat_description
    """Alias for :meth:`set_chat_description`"""
    pinChatMessage = pin_chat_message
    """Alias for :meth:`pin_chat_message`"""
    unpinChatMessage = unpin_chat_message
    """Alias for :meth:`unpin_chat_message`"""
    unpinAllChatMessages = unpin_all_chat_messages
    """Alias for :meth:`unpin_all_chat_messages`"""
    getCustomEmojiStickers = get_custom_emoji_stickers
    """Alias for :meth:`get_custom_emoji_stickers`"""
    getStickerSet = get_sticker_set
    """Alias for :meth:`get_sticker_set`"""
    uploadStickerFile = upload_sticker_file
    """Alias for :meth:`upload_sticker_file`"""
    createNewStickerSet = create_new_sticker_set
    """Alias for :meth:`create_new_sticker_set`"""
    addStickerToSet = add_sticker_to_set
    """Alias for :meth:`add_sticker_to_set`"""
    setStickerPositionInSet = set_sticker_position_in_set
    """Alias for :meth:`set_sticker_position_in_set`"""
    deleteStickerFromSet = delete_sticker_from_set
    """Alias for :meth:`delete_sticker_from_set`"""
    setStickerSetThumbnail = set_sticker_set_thumbnail
    """Alias for :meth:`set_sticker_set_thumbnail`"""
    setPassportDataErrors = set_passport_data_errors
    """Alias for :meth:`set_passport_data_errors`"""
    sendPoll = send_poll
    """Alias for :meth:`send_poll`"""
    stopPoll = stop_poll
    """Alias for :meth:`stop_poll`"""
    sendDice = send_dice
    """Alias for :meth:`send_dice`"""
    getMyCommands = get_my_commands
    """Alias for :meth:`get_my_commands`"""
    setMyCommands = set_my_commands
    """Alias for :meth:`set_my_commands`"""
    deleteMyCommands = delete_my_commands
    """Alias for :meth:`delete_my_commands`"""
    logOut = log_out
    """Alias for :meth:`log_out`"""
    copyMessage = copy_message
    """Alias for :meth:`copy_message`"""
    getChatMenuButton = get_chat_menu_button
    """Alias for :meth:`get_chat_menu_button`"""
    setChatMenuButton = set_chat_menu_button
    """Alias for :meth:`set_chat_menu_button`"""
    getMyDefaultAdministratorRights = get_my_default_administrator_rights
    """Alias for :meth:`get_my_default_administrator_rights`"""
    setMyDefaultAdministratorRights = set_my_default_administrator_rights
    """Alias for :meth:`set_my_default_administrator_rights`"""
    createInvoiceLink = create_invoice_link
    """Alias for :meth:`create_invoice_link`"""
    getForumTopicIconStickers = get_forum_topic_icon_stickers
    """Alias for :meth:`get_forum_topic_icon_stickers`"""
    createForumTopic = create_forum_topic
    """Alias for :meth:`create_forum_topic`"""
    editForumTopic = edit_forum_topic
    """Alias for :meth:`edit_forum_topic`"""
    closeForumTopic = close_forum_topic
    """Alias for :meth:`close_forum_topic`"""
    reopenForumTopic = reopen_forum_topic
    """Alias for :meth:`reopen_forum_topic`"""
    deleteForumTopic = delete_forum_topic
    """Alias for :meth:`delete_forum_topic`"""
    unpinAllForumTopicMessages = unpin_all_forum_topic_messages
    """Alias for :meth:`unpin_all_forum_topic_messages`"""
    editGeneralForumTopic = edit_general_forum_topic
    """Alias for :meth:`edit_general_forum_topic`"""
    closeGeneralForumTopic = close_general_forum_topic
    """Alias for :meth:`close_general_forum_topic`"""
    reopenGeneralForumTopic = reopen_general_forum_topic
    """Alias for :meth:`reopen_general_forum_topic`"""
    hideGeneralForumTopic = hide_general_forum_topic
    """Alias for :meth:`hide_general_forum_topic`"""
    unhideGeneralForumTopic = unhide_general_forum_topic
    """Alias for :meth:`unhide_general_forum_topic`"""
    setMyDescription = set_my_description
    """Alias for :meth:`set_my_description`"""
    setMyShortDescription = set_my_short_description
    """Alias for :meth:`set_my_short_description`"""
    getMyDescription = get_my_description
    """Alias for :meth:`get_my_description`"""
    getMyShortDescription = get_my_short_description
    """Alias for :meth:`get_my_short_description`"""
    setCustomEmojiStickerSetThumbnail = set_custom_emoji_sticker_set_thumbnail
    """Alias for :meth:`set_custom_emoji_sticker_set_thumbnail`"""
    setStickerSetTitle = set_sticker_set_title
    """Alias for :meth:`set_sticker_set_title`"""
    deleteStickerSet = delete_sticker_set
    """Alias for :meth:`delete_sticker_set`"""
    setStickerEmojiList = set_sticker_emoji_list
    """Alias for :meth:`set_sticker_emoji_list`"""
    setStickerKeywords = set_sticker_keywords
    """Alias for :meth:`set_sticker_keywords`"""
    setStickerMaskPosition = set_sticker_mask_position
    """Alias for :meth:`set_sticker_mask_position`"""
    setMyName = set_my_name
    """Alias for :meth:`set_my_name`"""
    getMyName = get_my_name
    """Alias for :meth:`get_my_name`"""
    unpinAllGeneralForumTopicMessages = unpin_all_general_forum_topic_messages
    """Alias for :meth:`unpin_all_general_forum_topic_messages`"""
