from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, NoReturn
from .version import *
import aiohttp
import asyncio
from aiohttp import ClientResponse
from typing import Any
from json import loads
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, NoReturn
from io import BufferedIOBase
from typing import List, Tuple
from itertools import groupby

if TYPE_CHECKING:
    from .Async import Bot

class HTTPClientError:
    USER_OR_CHAT_NOT_FOUND = "no such group or user"
    RATE_LIMIT = "bot limit exceed"
    LOCAL_RATE_LIMIT = "local_rate_limited"
    PERMISSION_DENIED = "permission_denied"

class Permissions:
    
    __slots__ = (
        "can_be_edited",
        "can_change_info",
        "can_post_messages",
        "can_edit_messages",
        "can_delete_messages",
        "can_invite_users",
        "can_restrict_members",
        "can_pin_messages",
        "can_promote_members",
        "can_send_messages",
        "can_send_media_messages"
    )

    def __init__(self, can_be_edited: bool = False, can_change_info: bool = False, can_post_messages: bool = False,
                 can_edit_messages: bool = False, can_delete_messages: bool = False, can_invite_users: bool = False,
                 can_restrict_members: bool = False, can_pin_messages: bool = False, can_promote_members: bool = False,
                 can_send_messages: bool = False, can_send_media_messages: bool = False):
        self.can_be_edited = can_be_edited
        self.can_change_info = can_change_info
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_delete_messages = can_delete_messages
        self.can_invite_users = can_invite_users
        self.can_restrict_members = can_restrict_members
        self.can_pin_messages = can_pin_messages
        self.can_promote_members = can_promote_members
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages

    @classmethod
    def from_dict(cls, data: dict):
        
        return cls(can_be_edited=data.get("can_be_edited", False), can_change_info=data.get("can_change_info", False),
                   can_post_messages=data.get("can_post_messages", False), can_edit_messages=data.get("can_edit_messages", False),
                   can_delete_messages=data.get("can_delete_messages", False), can_invite_users=data.get("can_invite_users", False),
                   can_restrict_members=data.get("can_restrict_members", False), can_pin_messages=data.get("can_pin_messages", False),
                   can_promote_members=data.get("can_promote_members", False), can_send_messages=data.get("can_send_messages", False),
                   can_send_media_messages=data.get("can_send_media_messages", False))

class ResponseStatusCode:
	OK = 200
	NOT_INCORRECT = 400
	NOT_FOUND = 440
	PERMISSION_DENIED = 403
	RATE_LIMIT = 429
     
async def json_or_text(response: "ClientResponse"):
	text = await response.text()

	try:
		json = loads(text)
	except JSONDecodeError:
		return text
	else:
		return json

class ResponseParser:
	

	__slots__ = (
		"result",
		"error_code",
		"description",
		"ok",
		"_raw"
	)

	def __init__(self, ok: bool, result: Any = None, error_code: int = None, description: str = None, raw: dict = None):
		self.ok = ok

		self.result = result
		self.error_code = error_code
		self.description = description
		self._raw = raw

	@classmethod
	async def from_response(cls, data: "ClientResponse"):
		data = await json_or_text(data)

		if isinstance(data, str):
			return cls(False, description=data, raw=dict(description=data))
		else:
			return cls(data.get("ok", False), data.get("result"), data.get("error_code"), data.get("description"), data)


class BaleError(Exception):
    
    __slots__ = (
        "message",
    )

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.__class__.__name__}\n('{self.message}')"

    def __reduce__(self):
        return self.__class__, (self.message,)

class InvalidToken(BaleError):
    
    __slots__ = ("_message",)

    def __init__(self, message):
        self._message = message

        super().__init__("Invalid Token" if self._message is not None else self._message)

class NotFound(BaleError):
    
    __slots__ = ()

    def __init__(self, message=None):
        super().__init__(message if message else "Not Found")

class Message:
    
    __slots__ = (
        "text", "caption", "from_user", "_author", "contact", "location", "chat", "message_id", "forward_from",
        "forward_from_chat", "forward_from_message_id", "date_code", "date",
        "edit_date", "audio", "document", "video", "photos", "location", "invoice", "new_chat_members",
        "left_chat_member", "reply_to_message",
        "invoice", "bot"
    )

    def __init__(self, message_id: str, date: datetime, text: Optional[str] = None, caption: Optional[str] = None,
                 forward_from: Optional["User"] = None, forward_from_chat: Optional["Chat"] = None,
                 forward_from_message_id: Optional[str] = None, from_user: Optional["User"] = None,
                 document: Optional["Document"] = None,
                 contact: Optional["ContactMessage"] = None, location: Optional["Location"] = None,
                 chat: Optional["Chat"] = None, video: Optional["Video"] = None,
                 photos: Optional[List["Photo"]] = None, reply_to_message: Optional["Message"] = None,
                 invoice: Optional["Invoice"] = None, audio: Optional["Audio"] = None,
                 bot: 'Bot' = None, **options):
        self.message_id: str = message_id if message_id is not None else None
        self.date = date if date is not None else None

        self.text: str | None = text if text is not None else None
        self.chat: Chat | None = chat if chat is not None else None
        self.reply_to_message: Message | None = reply_to_message if reply_to_message is not None else reply_to_message
        self.from_user: User | None = from_user if from_user is not None else None
        self.forward_from: User | None = forward_from if forward_from is not None else None
        self.forward_from_message_id: str = forward_from_message_id if forward_from_message_id is not None else None
        self.forward_from_chat: Chat | None = forward_from_chat if forward_from_chat is not None else None
        self.caption: str | None = caption if caption is not None else None
        self.document = document if document is not None else None
        self.video = video if video is not None else None
        self.audio = audio if audio is not None else None
        self.photos = photos if photos is not None else None
        self.contact: ContactMessage | None = contact if contact is not None else None
        self.location: Location | None = location if location is not None else None
        self.new_chat_members: List[User] | None = options.get("new_chat_members")
        self.left_chat_member: User | None = options.get("left_chat_member")
        self.invoice = invoice
        self.bot: Bot = bot if bot is not None else None

    @property
    def author(self):
        return self.from_user

    @property
    def attachment(self) -> Optional["File"]:
        attachment = self.video or self.photos or self.audio or self.document
        if not attachment:
            return

        if isinstance(attachment, list):
            attachment = attachment[0]

        return attachment.base_file

    @property
    def content(self) -> Optional[str]:
        return self.caption or self.text

    @content.setter
    def content(self, _value: str) -> NoReturn:
        if not isinstance(_value, str):
            raise TypeError("content must be type of str")

        if self.caption:
            self.caption = _value
        elif self.text:
            self.text = _value

    @property
    def chat_id(self) -> Optional[str | int]:
        return self.chat.chat_id

    @property
    def reply_to_message_id(self) -> Optional[str]:
        if not self.reply_to_message:
            return

        return self.reply_to_message.message_id


    @classmethod
    def from_dict(cls, data: dict, bot):
        options = {}
        if data.get("new_chat_members"):
            options["new_chat_members"] = [User.from_dict(bot=bot, data=i) for i in data.get("new_chat_members")]
        if data.get("left_chat_member"):
            options["left_chat_member"] = User.from_dict(bot=bot, data=data.get("left_chat_member"))

        return cls(bot=bot, message_id=str(data.get("message_id")),
                   chat=Chat.from_dict(bot=bot, data=data.get("chat")) if data.get("chat") else None,
                   reply_to_message=Message.from_dict(bot=bot, data=data.get("reply_to_message")) if data.get(
                       "reply_to_message") else None, date=datetime.fromtimestamp(int(data.get("date"))),
                   text=data.get("text"),
                   caption=data.get("caption"),
                   from_user=User.from_dict(bot=bot, data=data.get("from")) if data.get("from") else None,
                   forward_from=User.from_dict(bot=bot, data=data.get("forward_from")) if data.get(
                       "forward_from") else None,
                   forward_from_chat=Chat.from_dict(bot=bot, data=data.get("forward_from_chat")) if data.get(
                       "forward_from_chat") else None,
                   forward_from_message_id=str(data.get("forward_from_message_id")) if data.get(
                       "forward_from_message_id") else None,
                   document=Document.from_dict(bot=bot, data=data.get("document")) if data.get("document") else None,
                   contact=ContactMessage.from_dict(data=data.get("contact")) if data.get("contact") else None,
                   location=Location.from_dict(data=data.get("location")) if data.get("location") else None,
                   audio=Audio.from_dict(data=data.get("audio"), bot=bot) if data.get("audio") else None,
                   photos=[Photo.from_dict(data=photo_payload, bot=bot) for photo_payload in data.get("photo")] if data.get(
                       "photo") else None, video=Video.from_dict(data=data.get("video"), bot=bot) if data.get("video") else None,
                   invoice=Invoice.from_dict(data=data.get("invoice")) if data.get("invoice") else None, **options)

    def to_dict(self):
        data = {"message_id": self.message_id, "date": self.date, "text": self.text}

        if self.chat:
            data["chat"] = self.chat.to_dict()
        if self.from_user:
            data["from"] = self.from_user.to_dict()
        if self.caption:
            data["caption"] = self.caption
        if self.document:
            data["document"] = self.document.to_dict()
        if self.photos:
            data["photo"] = [photo.to_dict() for photo in self.photos]
        if self.video:
            data["video"] = self.video.to_dict()
        if self.audio:
            data["audio"] = self.audio.to_dict()
        if self.contact:
            data["contact"] = self.contact.to_dict()
        if self.location:
            data["location"] = self.location.to_dict()
        if self.new_chat_members:
            data["new_chat_members"] = self.new_chat_members
        if self.forward_from:
            data["forward_from"] = self.forward_from.to_dict()
        if self.forward_from_chat:
            data["forward_from"] = self.forward_from_chat.to_dict()
        if self.left_chat_member:
            data["left_chat_member"] = self.left_chat_member.to_dict()
        if self.reply_to_message_id:
            data["reply_to_message_id"] = self.reply_to_message_id

        return data

    async def reply(self, text: str, *, components: Optional[Components | RemoveMenuKeyboard] = None):
    
        return await self.bot.sendMessage(self.chat_id, text, components=components,
                                           reply_to_message_id=self.message_id if not self.chat.type.is_group_chat() else None)

    async def forward(self, chat_id: str | int):
        
        return await self.bot.forwardMessage(chat_id, self.chat_id, self.message_id)

    async def replyDocument(self, document: bytes | str | "Document", *, caption: Optional[str] = None):
        
        return await self.bot.sendDocument(self.chat_id, document, caption=caption,
                                            reply_to_message_id=self.message_id if not self.chat.type.is_group_chat() else None)

    async def replyPhoto(self, photo: bytes | str | "Photo", *, caption: Optional[str] = None):
        
        return await self.bot.sendPhoto(self.chat_id, photo, caption=caption,
                                         reply_to_message_id=self.message_id if not self.chat.type.is_group_chat() else None)

    async def replyVideo(self, video: bytes | str | "Video", *, caption: Optional[str] = None):
        
        return await self.bot.sendVideo(self.chat_id, video, caption=caption,
                                         reply_to_message_id=self.message_id if not self.chat.type.is_group_chat() else None)

    async def replyAudio(self, audio: bytes | str | "Audio", *, caption: Optional[str] = None):
        
        return await self.bot.sendAideo(self.chat_id, audio, caption=caption,
                                         reply_to_message_id=self.message_id if not self.chat.type.is_group_chat() else None)

    async def edit(self, text: str, *, components: "Components" | "RemoveMenuKeyboard" = None) -> Message:
        
        return await self.bot.editMessage(self.chat_id, self.message_id, text, components=components)

    async def delete(self):
        
        return await self.bot.deleteMessage(self.chat_id, self.message_id)

    def __str__(self):
        return str(self.message_id)

    def __eq__(self, other):
        return isinstance(other, Message) and self.message_id == other.message_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<Message message_id={self.message_id} from={self.from_user} chat={self.chat}>"
    
__all__ = (
    "UpdateType",
    "Update"
)


def parse_type(data: dict) -> "UpdateType":
    if data.get(UpdateType.CALLBACK):
        return UpdateType(UpdateType.CALLBACK)
    elif data.get(UpdateType.EDITED_MESSAGE):
        return UpdateType(UpdateType.EDITED_MESSAGE)
    elif data.get(UpdateType.MESSAGE):
        return UpdateType(UpdateType.MESSAGE)
    else:
        return UpdateType(UpdateType.UNKNOWN)


class UpdateType:
    
    MESSAGE = "message"
    CALLBACK = "callback_query"
    EDITED_MESSAGE = "edited_message"
    UNKNOWN = "unknown"

    __slots__ = (
        "_type",
    )

    def __init__(self, _type: str):
        self._type = _type

    @property
    def type(self) -> str:
        return self._type

    def isMessageUpdate(self):
        
        return self._type == self.MESSAGE

    def isCallbackUpdate(self):
        
        return self._type == self.CALLBACK

    def isEditedMessage(self):
        
        return self._type == self.EDITED_MESSAGE

    def isUnknownUpdate(self):
        
        return self._type == self.UNKNOWN

    def __str__(self):
        return self._type

    def __eq__(self, other):
        return self._type == other

    def __ne__(self, other):
        return not self.__eq__(other)

class Update:
  
    __slots__ = (
        "update_id",
        "type",
        "message",
        "callback_query",
        "edited_message",
        "bot"
    )

    def __init__(self, update_id: int, type: "UpdateType", callback_query: "CallbackQuery" = None, message: "Message" = None,
                 edited_message: "Message" = None, bot: 'Bot' = None):
        self.update_id = int(update_id)
        self.type = type
        self.bot = bot
        self.callback_query = callback_query if callback_query is not None else None
        self.message = message if message is not None else None
        self.edited_message = edited_message if edited_message is not None else None

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        callback_query, message, edited_message = None, None, None
        parsed_type: UpdateType = parse_type(data)

        if parsed_type.isCallbackUpdate():
            callback_query = CallbackQuery.from_dict(data.get("callback_query"), bot=bot)
        if parsed_type.isMessageUpdate():
            message = Message.from_dict(data.get("message"), bot=bot)
        if parsed_type.isEditedMessage():
            edited_message = Message.from_dict(data.get("edited_message"), bot=bot)

        return cls(type=parsed_type, update_id=data["update_id"],
                   message=message, callback_query=callback_query, edited_message=edited_message, bot=bot)

    def to_dict(self) -> dict:
        data = {}

        if self.type:
            data["type"] = self.type
        if self.callback_query:
            data["callback_query"] = self.callback_query.to_dict()
        if self.message:
            data["message"] = self.message.to_dict()

        return data

    def __eq__(self, other):
        return isinstance(other, Update) and self.update_id == other.update_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id <= other.update_id

    def __ge__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id >= other.update_id

    def __lt__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id < other.update_id

    def __gt__(self, other):
        return not self.__lt__(other)

    def __repr__(self):
        return f"<Update update_id={self.update_id} type={self.type}>"
    
class User:
    
    __slots__ = (
        "is_bot",
        "first_name",
        "last_name",
        "username",
        "user_id",
        "bot"
    )

    def __init__(self, user_id: int, is_bot: bool, first_name: str, last_name: Optional[str] = None, username: Optional[str] = None,
            bot: 'Bot' = None):
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_id = user_id
        self.bot = bot

    @property
    def mention(self) -> str | None:
        return f"@{self.username}" if self.username else None

    @property
    def chat_id(self) -> str:
        return str(self.user_id)

    async def send(self, text: str, components: Optional["Components" | "RemoveMenuKeyboard"] =None):
       
        return await self.bot.sendMessage(self.chat_id, text, components=components)

    async def sendDocument(self, document: bytes | str | "Document", *, caption: Optional[str] = None):
        
        return await self.bot.sendDocument(self.chat_id, document, caption=caption)

    async def sendPhoto(self, photo: bytes | str | "Photo", *, caption: Optional[str] = None):
        
        return await self.bot.sendPhoto(self.chat_id, photo, caption=caption)

    async def sendVideo(self, video: bytes | str | "Video", *, caption: Optional[str] = None):
        
        return await self.bot.sendVideo(self.chat_id, video, caption=caption)

    async def sendAudio(self, audio: bytes | str | "Audio", *, caption: Optional[str] = None):
        
        return await self.bot.sendAudio(self.chat_id, audio, caption=caption)

    async def sendLocation(self, location: "Location"):
        
        return await self.bot.sendLocation(self.chat_id, location)

    async def sendContact(self, contact: "ContactMessage"):
        
        return await self.bot.sendContact(self.chat_id, contact)

    async def sendVoice(self, title: str, description: str, provider_token: str, prices: List["Price"], *, photo_url: Optional[str] = None,
               need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False, need_email: Optional[bool] = False,
               need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True):
        
        return await self.bot.sendVoice(self.chat_id, title, description, provider_token, prices,
                                           photo_url=photo_url, need_name=need_name, need_email=need_email,
                                           need_phone_number=need_phone_number, need_shipping_address=need_shipping_address, is_flexible=is_flexible)

    @classmethod
    def from_dict(cls, data: dict, bot=None):
        return cls(is_bot=data.get("is_bot"), username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   user_id=data.get("id"), bot=bot)

    def to_dict(self):
        data = {"is_bot": self.is_bot,
                "first_name": self.first_name if self.first_name is not None else None,
                "last_name": self.last_name if self.last_name is not None else None,
                "username": self.username if self.username is not None else None,
                "id": self.user_id if self.user_id is not None else None}

        return data

    def __str__(self):
        return (str(self.username) + "#" + str(self.user_id) if self.username else str(self.first_name) + " " + str(
            self.last_name))

    def __eq__(self, other: User):
        return isinstance(other, User) and self.user_id == other.user_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return f"<User is_bot={self.is_bot} first_name={self.first_name} last_name={self.last_name} user_id={self.user_id} username={self.username}>"

class Components:
    __slots__ = (
        "_menu_keyboards",
        "_inline_keyboards"
    )

    def __init__(self):
        self._menu_keyboards: List[Tuple["MenuKeyboard", int]] = []
        self._inline_keyboards: List[Tuple["InlineKeyboard", int]] = []

    @property
    def menu_keyboards(self) -> List["MenuKeyboard"]:
        return [item[0] for item in self._menu_keyboards]

    @property
    def inline_keyboards(self) -> List["InlineKeyboard"]:
        return [item[0] for item in self._inline_keyboards]

    def add_menu_keyboard(self, menu_keyboard: "MenuKeyboard", row: int = 1):
        
        if not isinstance(menu_keyboard, MenuKeyboard):
            raise TypeError("menu_keyboard param must be type of MenuKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._menu_keyboards.append((menu_keyboard, row))

    def remove_menu_keyboard(self, menu_keyboard: "MenuKeyboard", row: int = 1):
        
        if not isinstance(menu_keyboard, MenuKeyboard):
            raise TypeError("menu_keyboard param must be type of MenuKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._menu_keyboards.remove((menu_keyboard, row))

    def add_inline_keyboard(self, inline_keyboard: "InlineKeyboard", row: int = 1):
        
        if not isinstance(inline_keyboard, InlineKeyboard):
            raise TypeError("inline_keyboard param must be type of InlineKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._inline_keyboards.append((inline_keyboard, row))

    def remove_inline_keyboard(self, inline_keyboard: "InlineKeyboard", row: int = 1):
        
        if not isinstance(inline_keyboard, InlineKeyboard):
            raise TypeError("inline_keyboard param must be type of InlineKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._inline_keyboards.remove((inline_keyboard, row))

    def to_dict(self):
        is_used_menu_keyboard = bool(self._menu_keyboards)
        is_used_inline_keyboard = bool(self._inline_keyboards)

        if is_used_menu_keyboard and is_used_inline_keyboard:
            raise TypeError("you can't use menu keyboards and inline keyboards params together.")

        if not (is_used_menu_keyboard or is_used_inline_keyboard):
            raise TypeError("you must be use menu keyboards or inline keyboards param.")

        correct_children = self._menu_keyboards if bool(self._menu_keyboards) else self._inline_keyboards
        correct_children_name = "keyboard" if bool(self._menu_keyboards) else "inline_keyboard"
        def key(item: Tuple["InlineKeyboard" | "MenuKeyboard", int]):
            return item[1] or 1

        sorted_components = sorted(correct_children, key=key)
        payload = {correct_children_name: []}

        for _, group in groupby(sorted_components, key=key):
            _components = []
            for item in group:
                component = item[0]
                _components.append(component.to_dict())

            payload[correct_children_name].append(_components)

        return payload
    
class MenuKeyboard:
    
    __slots__ = (
        "text",
        "request_contact",
        "request_location"
    )

    def __init__(self, text: str, request_contact: Optional[bool] = False, request_location: Optional[bool] = False):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location

    @classmethod
    def from_dict(cls, data: dict):
        return cls(text=data["text"], request_contact=data.get("request_contact", False), request_location=data.get("request_location", False))

    def to_dict(self):
        data = {
            "text": self.text
        }

        if self.request_contact:
            data["request_contact"] = self.request_contact
        if self.request_location:
            data["request_location"] = self.request_location
        return data


class RemoveMenuKeyboard:
    
    def to_dict(self) -> dict:
        return {"keyboard": None}
    
class Chat:
    
    __slots__ = (
        "chat_id",
        "type",
        "title",
        "username",
        "first_name",
        "last_name",
        "pinned_message",
        "all_members_are_administrators",
        "invite_link",
        "bot"
    )

    def __init__(self, chat_id: int | str, type: "ChatType", title: Optional[str] = None, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None,
                 pinned_message: Optional["Message"] = None, all_members_are_administrators: Optional[bool] = None, invite_link: Optional[str] = None, bot: 'Bot' = None):
        self.chat_id = chat_id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.pinned_message = pinned_message
        self.all_members_are_administrators = all_members_are_administrators
        self.invite_link = invite_link
        self.bot = bot

    @property
    def mention(self) -> str | None:
        return ("@" + self.username) if self.username else None

    async def send(self, text: str, components: Optional["Components" | "RemoveMenuKeyboard"] = None):
        
        return await self.bot.sendMessage(self.chat_id, text, components=components)

    async def sendDocument(self, document: bytes | str | "Document", *, caption: Optional[str] = None):
        
        return await self.bot.sendDocument(self.chat_id, document, caption=caption)

    async def sendPhoto(self, photo: bytes | str | "Photo", *, caption: Optional[str] = None):
        
        return await self.bot.sendPhoto(self.chat_id, photo, caption=caption)

    async def sendVideo(self, video: bytes | str | "Video", *, caption: Optional[str] = None):
        
        return await self.bot.sendVideo(self.chat_id, video, caption=caption)

    async def sendAudio(self, audio: bytes | str | "Audio", *, caption: Optional[str] = None):
        
        return await self.bot.sendAudio(self.chat_id, audio, caption=caption)

    async def sendLocation(self, location: "Location"):
        
        return await self.bot.sendLocation(self.chat_id, location)

    async def sendContact(self, contact: "ContactMessage") -> "Message":
        
        return await self.bot.sendContact(self.chat_id, contact)

    async def sendVoice(self, title: str, description: str, provider_token: str, prices: List["Price"], *,
                   photo_url: Optional[str] = None, need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False,
                       need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True):
        
        return await self.bot.sendVoice(self.chat_id, title, description, provider_token, prices,
                                        photo_url=photo_url, need_name=need_name, need_email=need_email,
                                        need_phone_number=need_phone_number, need_shipping_address=need_shipping_address, is_flexible=is_flexible)

    async def leave(self):
        
        await self.bot.leaveChat(self.chat_id)

    async def addMember(self, user: "User"):
        
        await self.bot.invite_user(self.chat_id, user.chat_id)

    async def getChatMember(self, user: "User" | str):
        
        if not isinstance(user, (User, str)):
            raise TypeError("user must be type of User or str")

        if isinstance(user, User):
            user = user.user_id

        return await self.bot.getChatMember(self.chat_id, user_id=user)

    async def banChatMember(self, user: "User" | str):
        
        if not isinstance(user, (User, str)):
            raise TypeError("user must be type of user or str")

        if isinstance(user, User):
            user = user.user_id

        return await self.bot.banChatMember(self.chat_id, user_id=user)

    async def getChatMembersCount(self):
        
        return await self.bot.getChatMembersCount(self.chat_id)

    async def getChatAdministrators(self):
        
        return await self.bot.getChatAdministrators(self.chat_id)

    @classmethod
    def from_dict(cls, data: dict, bot):
        return cls(bot=bot, chat_id=data.get("id"), type=ChatType(data.get("type")), title=data.get("title"),
                   username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   pinned_message=Message.from_dict(bot=bot, data=data.get("pinned_message")) if data.get("pinned_message") else None,
                   all_members_are_administrators=data.get("all_members_are_administrators", True),
                   invite_link=data.get("invite_link"))

    def to_dict(self):
        data = {
            "id": self.chat_id,
            "type": self.type,
            "title": self.title,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name
        }

        return data

    def __str__(self):
        return str(self.first_name) + str(self.last_name)

    def __eq__(self, other):
        return isinstance(other, Chat) and self.chat_id == other.chat_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return (f"<Chat type={self.type} first_name={self.first_name} last_name={self.last_name} user_id={self.chat_id} username={self.username}"
            f"title={self.title}>")

class ChatType:
    
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"

    __slots__ = (
        "_type",
    )

    def __init__(self, _type: str):
        self._type = _type

    @property
    def type(self) -> str:
        return self._type

    def is_private_chat(self):
        
        return self._type == self.PRIVATE

    def is_group_chat(self):
        
        return self._type == self.GROUP

    def is_channel_chat(self):
        
        return self._type == self.CHANNEL

    def __repr__(self):
        return f"<ChatType type={self.type}>"

    def __eq__(self, other):
        return self._type == other

    def __ne__(self, other):
        return not self.__eq__(other)
    
class Price:
	
	__slots__ = ("label", "amount")

	def __init__(self, label: str = None, amount: int = None):
		self.label = label
		self.amount = amount

	@classmethod
	def from_dict(cls, data):
		return cls(label=data["label"], amount=data["amount"])

	def to_dict(self):
		data: dict[str, int | str] = {
			"label": self.label,
			"amount": self.amount
		}
		return data
    
class ChatMember:
    
    __slots__ = (
        "chat_id", "status", "user", "permissions", "bot"
    )

    def __init__(self, chat_id: int, status: "ChatMemberStatus", user: "User", permissions: "Permissions", bot: "Bot"):
        self.chat_id = chat_id
        self.status = status
        self.user = user
        self.permissions = permissions
        self.bot = bot

    async def ban(self):
        
        return await self.bot.banChatMember(self.chat_id, self.user.user_id)

    @classmethod
    def from_dict(cls, chat_id: int, data: dict, bot: "Bot"):
        return cls(chat_id=chat_id, permissions=Permissions.from_dict(data), user=User.from_dict(data.get("user")),
                   status=ChatMemberStatus(data.get("status")), bot=bot)

    def __repr__(self):
        return f"<ChatMember chat_id={self.chat_id} status={self.status} user={self.user} permissions={self.permissions}>"

class ChatMemberStatus:

    OWNER = "creator"
    ADMIN = "administrator"
    MEMBER = "member"
    CREATOR = OWNER
    __slots__ = ("_status",)

    def __init__(self, _status: str):
        self._status = _status

    @property
    def status(self) -> str:
        return self._status

    def isOwner(self):
        
        return self._status == self.OWNER

    def isAdmin(self):
        
        return self._status == self.ADMIN

    def isMember(self):
        
        return self._status == self.MEMBER

    def __repr__(self):
        return f"<MemberRole role={self.status}>"

    def __eq__(self, other):
        return self._status == other

    def __ne__(self, other):
        return not self.__eq__(other)
    
__all__ = ("HTTPClient", "Route")

class Route:
	
	__slots__ = (
		"method",
		"endpoint",
		"token"
	)

	def __init__(self, method: str, endpoint: str, token: str):
		if not isinstance(token, str):
			raise TypeError("token param must be str.")
		self.method = method
		self.endpoint = endpoint
		self.token = token

	@property
	def url(self):
		
		return "{base_url}bot{token}/{endpoint}".format(base_url = BALE_API_BASE_URL, token = self.token, endpoint = self.endpoint)

class HTTPClient:
	

	__slots__ = (
		"_loop",
		"token",
		"__session"
	)

	def __init__(self, loop, token):
		self.__session = None
		self._loop: asyncio.AbstractEventLoop = loop
		self.token = token

	def is_closed(self):
		return self.__session is None

	@property
	def loop(self):
		return self._loop

	@loop.setter
	def loop(self, _value):
		self._loop = _value

	def reload_session(self):
		
		if self.__session and self.__session.closed:
			self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def start(self):
		
		if self.__session:
			raise RuntimeError("HTTPClient started ")
		self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def close(self):
		
		if self.__session:
			await self.__session.close()
			self.__session = None

	async def request(self, route: Route, **kwargs):
		url = route.url
		method = route.method
		for tries in range(5):
			try:
				async with self.__session.request(method=method, url=url, **kwargs) as response:
					response: aiohttp.ClientResponse = response
					parsed_response = await ResponseParser.from_response(response)
					if response.status == ResponseStatusCode.OK:
						return parsed_response
					elif response.status == ResponseStatusCode.NOT_FOUND:
						raise NotFound(parsed_response.description)
					elif response.status == ResponseStatusCode.PERMISSION_DENIED:
						raise Forbidden()
					elif not parsed_response.ok or response.status in (ResponseStatusCode.NOT_INCORRECT, ResponseStatusCode.RATE_LIMIT):
						if parsed_response.description == HTTPClientError.USER_OR_CHAT_NOT_FOUND:
							raise NotFound("User or Chat not Found")
						elif response.status == ResponseStatusCode.RATE_LIMIT or parsed_response.description in (HTTPClientError.RATE_LIMIT, HTTPClientError.LOCAL_RATE_LIMIT):
							if tries >= 4:
								raise RateLimited()

							await asyncio.sleep((1 + tries) * 2)
							continue
						elif parsed_response.description == HTTPClientError.PERMISSION_DENIED:
							raise Forbidden()

						raise APIError(
								str(parsed_response.error_code), parsed_response.description
							)
			except aiohttp.ClientConnectorError as error:
				raise NetworkError(str(error))
			except aiohttp.ServerTimeoutError:
				raise TimeOut()
			except aiohttp.ClientOSError as error:
				raise BaleError(str(error))
			except Exception as error:
				raise HTTPException(error)

	async def getFile(self, file_id):
		async with self.__session.get("{base_file_url}/bot{token}/{file_id}".format(base_file_url = BALE_API_FILE_URL, token = self.token, file_id = file_id)) as response:
			if response.status == ResponseStatusCode.OK:
				return await response.read()
			elif response.status in (ResponseStatusCode.NOT_INCORRECT, ResponseStatusCode.NOT_FOUND):
				raise NotFound("File is not Found")
			elif response.status == ResponseStatusCode.PERMISSION_DENIED:
				raise Forbidden()
			else:
				error_payload = await response.json()
				raise APIError(0, "UNKNOWN ERROR: {}".format(error_payload))

		raise RuntimeError("failed to get file")

	def sendMessage(self, chat_id, text, *, components=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"text": text
		}
		if components:
			payload["reply_markup"] = components
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendMessage", self.token), json=payload)

	def forwardMessage(self, chat_id, from_chat_id, message_id):
		payload = {
			"chat_id": chat_id,
			"from_chat_id": from_chat_id,
			"message_id": message_id
		}

		return self.request(Route("POST", "forwardMessage", self.token), json=payload)

	def sendDocument(self, chat_id, document, *, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"document": document
		}
		if caption:
			payload["caption"] = caption

		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "Senddocument", self.token), data=payload)

	def sendPhoto(self, chat_id, photo, *, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"photo": photo
		}
		if caption:
			payload["caption"] = caption
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "SendPhoto", self.token), data=payload)

	def sendVideo(self, chat_id, video, *, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"video": video
		}
		if caption:
			payload["caption"] = caption
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendVideo", self.token), data=payload)

	def sendAudio(self, chat_id, audio, *, caption=None, duration=None, title=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"audio": audio
		}
		if caption:
			payload["caption"] = caption
		if duration:
			payload["duration"] = duration
		if title:
			payload["title"] = title
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "SendAudio", self.token), data=payload)

	def sendContact(self, chat_id, phone_number, first_name, *, last_name):
		payload = {
			"chat_id": chat_id,
			"phone_number": phone_number,
			"first_name": first_name
		}
		if last_name:
			payload["last_name"] = last_name

		return self.request(Route("POST", "SendContact", self.token), data=payload)

	def sendVoice(self, chat_id, title, description, provider_token, prices, photo_url=None, need_name=False, need_phone_number=False, need_email=False, need_shipping_address=False, is_flexible=True):
		payload = {"chat_id": chat_id, "title": title, "description": description, "provider_token": provider_token, "prices": prices}
		if photo_url:
			payload["photo_url"] = photo_url
		payload["need_name"] = need_name
		payload["need_phone_number"] = need_phone_number
		payload["need_email"] = need_email
		payload["need_shipping_address"] = need_shipping_address
		payload["is_flexible"] = is_flexible

		return self.request(Route("POST", "sendInvoice", self.token), json=payload)

	def sendLocation(self, chat_id, latitude, longitude):
		payload = { "chat_id": chat_id, "latitude": latitude, "longitude": longitude}

		return self.request(Route("POST", "sendLocation", self.token), json=payload)

	def editMessage(self, chat_id, message_id, text, *, components=None):
		payload = {
			"chat_id": chat_id,
			"message_id": message_id,
			"text": text
		}
		if components:
			payload["reply_markup"] = components

		return self.request(Route("POST", "editMessageText", self.token), json=payload)

	def deleteMessage(self, chat_id, message_id):
		payload = {
			"chat_id": chat_id,
			"message_id": message_id
		}
		return self.request(Route("GET", "deletemessage", self.token), params=payload)

	def getUpdates(self, offset=None, limit=None):
		payload = {}
		if offset:
			payload["offset"] = offset
		if limit:
			payload["limit"] = limit
		return self.request(Route("POST", "getupdates", self.token), json=payload)

	def delete_webhook(self):
		return self.request(Route("GET", "deleteWebhook", self.token))

	def get_Bot(self):
		return self.request(Route("GET", "getme", self.token))

	def getChat(self, chat_id):
		return self.request(Route("GET", "getchat", self.token), params=dict(chat_id=chat_id))

	def leaveChat(self, chat_id):
		return self.request(Route("GET", "leaveChat", self.token), params=dict(chat_id=chat_id))

	def getChatAdministrators(self, chat_id):
		return self.request(Route("GET", "getChatAdministrators", self.token), params=dict(chat_id=chat_id))

	def getChatMembersCount(self, chat_id):
		return self.request(Route("GET", "getChatMemberCount", self.token), params=dict(chat_id=chat_id))

	def getChatMember(self, chat_id, member_id):
		return self.request(Route("GET", "getChatMember", self.token), params=dict(chat_id=chat_id, user_id=member_id))

	def banChatMember(self, chat_id, member_id):
		return self.request(Route("POST", "banChatMember", self.token), params=dict(chat_id=chat_id, user_id=member_id))

	def inviteToChat(self, chat_id, user_id):
		return self.request(Route("GET", "InviteUser", self.token), json=dict(chat_id=chat_id, user_id=user_id))

__all__ = (
    "Updater",
    "EventType"
)


class EventType:
    
    READY = "on_ready"
    BEFORE_READY = "on_before_ready"
    UPDATE = "on_update"
    MESSAGE = "on_message"
    EDITED_MESSAGE = "on_edited_message"
    CALLBACK = "on_callback"
    MEMBER_CHAT_JOIN = "on_member_chat_join"
    MEMBER_CHAT_LEAVE = "on_member_chat_leave"


class Updater:
    
    __slots__ = (
        "bot",
        "_last_offset",
        "_is_running",
        "__lock",
        "interval"
    )

    def __init__(self, bot: "Bot"):
        self.bot = bot
        self._last_offset = None
        self._is_running = False
        self.__lock = asyncio.Lock()
        self.interval = None

    async def start(self, sleep_after_every_get_updates: int = None):
       
        if self._is_running:
            raise RuntimeError("Updater is running")
        self.interval = sleep_after_every_get_updates
        self.bot.dispatch("before_ready")
        await self.polling()

    async def polling(self):
        async with self.__lock:
            if self._is_running:
                raise RuntimeError("Updater is running")

            if self.bot.http.is_closed():
                raise RuntimeError("HTTPClient is Closed")

            self._is_running = True

            try:
                await self._polling()
            except Exception as exc:
                self._is_running = False
                raise exc

    async def _polling(self):
        self.bot.dispatch("ready")
        await self.actionGetUpdates()

    async def actionGetUpdates(self):
        while self._is_running:
            try:
                updates = await self.bot.getUpdates(offset=self._last_offset)
            except Exception as exc:
                await self.bot.on_error("getUpdates", exc)
            else:
                if updates:
                    for update in updates:
                        await self.CallToDispatch(update)

                    self._last_offset = updates[-1].update_id
                if self.interval:
                    await asyncio.sleep(self.interval)

    async def CallToDispatch(self, update: "Update"):
        self.bot.dispatch("update", update)
        if update.type.isCallbackUpdate():
            self.bot.dispatch("callback", update.callback_query)
        elif update.type.isMessageUpdate():
            self.bot.dispatch("message", update.message)
            if update.message.left_chat_member:
                self.bot.dispatch("member_chat_leave", update.message, update.message.chat, update.message.left_chat_member)
            for user in update.message.new_chat_members or []:
                self.bot.dispatch("member_chat_join", update.message, update.message.chat, user)
        elif update.type.isEditedMessage():
            self.bot.dispatch("edited_message", update.edited_message)

    async def stop(self):
        
        async with self.__lock:
            if not self._is_running:
                raise RuntimeError("Updater is not running")

            self._is_running = False

class CallbackQuery:
    
    __slots__ = (
        "callback_id",
        "from_user",
        "message",
        "inline_message_id",
        "data",
        "bot"
    )

    def __init__(self, callback_id: int, data: str = None, message: "Message" = None,
                 inline_message_id: str = None, from_user: "User" = None, bot: "Bot" = None):
        self.callback_id = callback_id
        self.data = data
        self.message = message
        self.inline_message_id = inline_message_id
        self.from_user = from_user
        self.bot = bot

    @property
    def user(self):
        
        return self.from_user

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        return cls(bot=bot, data=data.get("data"), callback_id=data.get("id"), message=Message.from_dict(data.get("message"), bot=bot),
                   inline_message_id=data.get("inline_message_id"),
                   from_user=User.from_dict(bot=bot, data=data.get("from")))

    def to_dict(self):
        data = {
            "id": self.callback_id
        }

        if self.data:
            data["data"] = self.data
        if self.inline_message_id:
            data["inline_message_id"] = self.inline_message_id
        if self.message:
            data["message"] = self.message.to_dict()
        if self.from_user:
            data["from_user"] = self.from_user.to_dict()

        return data

    def __eq__(self, other):
        return isinstance(other, CallbackQuery) and self.callback_id == other.callback_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<CallbackQuery inline_message_id={self.inline_message_id} message={self.message} from_user={self.from_user} data={self.data}>"

class HTTPClientError:
    USER_OR_CHAT_NOT_FOUND = "no such group or user"
    RATE_LIMIT = "bot limit exceed"
    LOCAL_RATE_LIMIT = "local_rate_limited"
    PERMISSION_DENIED = "permission_denied"

class BaleError(Exception):
    
    __slots__ = (
        "message",
    )

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.__class__.__name__}\n('{self.message}')"

    def __reduce__(self):
        return self.__class__, (self.message,)


class InvalidToken(BaleError):
    
    __slots__ = ("_message",)

    def __init__(self, message):
        self._message = message

        super().__init__("Invalid Token" if self._message is not None else self._message)


class APIError(BaleError):
    
    __slots__ = ()

    def __init__(self, error_code, message):
        super().__init__("{}: {}".format(error_code, message))


class NetworkError(BaleError):
    
    __slots__ = ()


class TimeOut(BaleError):
    __slots__ = ()

    def __init__(self):
        super().__init__("Time Out")


class NotFound(BaleError):
    
    __slots__ = ()

    def __init__(self, message=None):
        super().__init__(message if message else "Not Found")


class Forbidden(BaleError):
    
    __slots__ = ()

    def __init__(self):
        super().__init__("Forbidden")

class RateLimited(BaleError):
    
    __slots__ = ()

    def __init__(self):
        super().__init__("We are Rate Limited")

class HTTPException(BaleError):
    
    __slots__ = ()

    def __init__(self, error):
        super().__init__(str(error))

class File:
    
    __slots__ = (
        "file_type",
        "file_id",
        "file_size",
        "mime_type",
        "extra",
        "bot"
    )
    def __init__(self, file_type, file_id, file_size, mime_type, bot: "Bot", **kwargs):
        self.file_type = file_type
        self.file_id = file_id
        self.file_size = file_size
        self.mime_type = mime_type
        self.extra = kwargs
        self.bot = bot

    @property
    def type(self) -> str:
        
        return self.file_type

    @property
    def base_file(self) -> "File":
        return File(self.file_type, self.file_id, self.file_size, self.mime_type, self.bot, **self.extra)

    async def get(self) -> bytes:
        
        return await self.bot.getFile(self.file_id)

    async def save_to_memory(self, out: "BufferedIOBase") -> NoReturn:
        
        buf = await self.get()

        out.write(buf)

    def to_dict(self):
        data = {"file_id": self.file_id, "file_size": self.file_size, "mime_type": self.mime_type,
                **self.extra}

        return data

    def __len__(self):
        return self.file_size

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.file_id == other.file_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<File file_type={self.file_type} file_id={self.file_id} file_size={self.file_size} >"

    def __str__(self):
        return self.file_id


class Photo(File):
    
    __FILE_TYPE__ = "PHOTO"
    __slots__ = File.__slots__ + (
        "width",
        "height"
    )
    def __init__(self, file_id: str, width: int, height: int, file_size: int, bot: "Bot"):
        super().__init__(self.__FILE_TYPE__, file_id, file_size, "jpg", bot, width = width, height = height)

        self.width = width
        self.height = height

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        return cls(
            file_id=data.get("file_id"),
            width=data.get("width"),
            height=data.get("height"),
            file_size=data.get("file_size"),
            bot=bot
        )
    
class Document(File):
	
	__FILE_TYPE__ = "DOCUMENT"
	__slots__ = File.__slots__ + (
		"file_name",
	)

	def __init__(self, file_id: str, file_name: str = None, mime_type: str = None, file_size: int = None,
	             bot: "Bot" = None):
		super().__init__(self.__FILE_TYPE__, file_id, file_size, mime_type, bot, file_name=file_name)
		self.file_name = file_name if file_name is not None else None

	@classmethod
	def from_dict(cls, data: dict, bot: "Bot" = None):
		return cls(file_id=data.get("file_id"), file_name=data.get("file_name"),
		           mime_type=data.get("mime_type"), file_size=data.get("file_size"), bot=bot)

class Location:
    
    __slots__ = (
        "longitude",
        "latitude"
    )

    def __init__(self, longitude: int, latitude: int):
        self.longitude = longitude
        self.latitude = latitude

    @property
    def link(self) -> str:
        
        return f"https://maps.google.com/maps?q=loc:{self.longitude},{self.latitude}"

    @classmethod
    def from_dict(cls, data):
        return cls(longitude=data["longitude"], latitude=data["latitude"])

    def to_dict(self):
        data = {"longitude": self.longitude if self.longitude is not None else None,
                "latitude": self.latitude if self.latitude is not None else None}
        return data

    def __eq__(self, other):
        return isinstance(other, Location) and self.link == other.link

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<Location longitude={self.longitude} latitude={self.latitude} >"

class ContactMessage:
    
    __slots__ = (
        "phone_number",
        "first_name",
        "last_name",
        "bot"
    )

    def __init__(self, phone_number: int, first_name: str = None, last_name: str = None):
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def from_dict(cls, data: dict):
        return cls(first_name=data["first_name"], last_name=data["last_name"], phone_number=data["phone_number"])

    def to_dict(self):
        data = {"phone_number": self.phone_number, "first_name": self.first_name, "last_name": self.last_name}

        return data

    def __eq__(self, other):
        return isinstance(other, ContactMessage) and self.phone_number == other.phone_number

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<ContactMessage phone_number={self.phone_number} first_name={self.first_name} last_name={self.last_name} >"

class Video(File):
    
    __FILE_TYPE__ = "VIDEO"
    __slots__ = File.__slots__ + (
        "width",
        "height",
        "duration"
    )

    def __init__(self, file_id: str, mime_type: str, width: int, height: int, file_size: int, duration: int, bot: "Bot"):
        super().__init__(self.__FILE_TYPE__, file_id, file_size, mime_type, bot, duration = duration, width = width, height = height)

        self.width = width
        self.height = height
        self.duration = duration

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        return cls(
            file_id=data.get("file_id"),
            width=data.get("width"),
            height=data.get("height"),
            file_size=data.get("file_size"),
            duration=data.get("duration"),
            mime_type=data.get("mime_type"),
            bot=bot
        )
    
class Audio(File):
    
    __FILE_TYPE__ = "AUDIO"
    __slots__ = File.__slots__ + (
        "duration",
        "title"
    )

    def __init__(self, file_id: str, duration: int = None, file_size: int = None, bot: "Bot" = None, mime_type: str = None, title: str = None):
        super().__init__(self.__FILE_TYPE__, file_id, file_size, mime_type, bot, duration=duration, title=title)

        self.duration = duration
        self.title = title

    @classmethod
    def from_dict(cls, data, bot: "Bot"):
        return cls(file_id=data["file_id"], duration=data["duration"], file_size=data["file_size"], title=data["title"],
                   mime_type=data["mime_type"], bot=bot)
    
class Invoice:
	
	__slots__ = (
		"title",
		"description",
		"start_parameter",
		"currency",
		"total_amount"
	)
	def __init__(self, title: str, description: str, start_parameter: str, currency: str, total_amount: int):
		self.title = title
		self.description = description
		self.start_parameter = start_parameter
		self.currency = currency
		self.total_amount = total_amount

	@classmethod
	def from_dict(cls, data: dict):
		return cls(
			title=data.get("title"),
			description=data.get("description"),
			start_parameter=data.get("start_parameter"),
			currency=data.get("currency"),
			total_amount=data.get("total_amount")
		)

class InlineKeyboard:
    
    __slots__ = (
        "text", "callback_data", "url", "switch_inline_query", "switch_inline_query_current_chat"
    )

    def __init__(self, text: str, *, callback_data: str = None, url: str = None, switch_inline_query: str = None,
                 switch_inline_query_current_chat: str = None):
        self.text = text
        self.callback_data = callback_data if callback_data is not None else None
        self.url = url if url is not None else None
        self.switch_inline_query = switch_inline_query if switch_inline_query is not None else switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat if switch_inline_query_current_chat is not None else None

    @classmethod
    def from_dict(cls, data: dict):
        if not data.get("text") or not data.get("callback_data"):
            return None
        return cls(text=data["text"], callback_data=data.get("callback_data"), url=data.get("url"),
                   switch_inline_query=data.get("switch_inline_query"),
                   switch_inline_query_current_chat=data.get("switch_inline_query_current_chat"))

    def to_dict(self) -> dict:
        data = {
            "text": self.text
        }

        if self.callback_data:
            data["callback_data"] = self.callback_data

        if self.url:
            data["url"] = self.url

        if self.switch_inline_query:
            data["switch_inline_query"] = self.switch_inline_query

        if self.switch_inline_query_current_chat:
            data["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat

        return data
