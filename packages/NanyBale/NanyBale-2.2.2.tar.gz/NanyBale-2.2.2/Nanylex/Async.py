from __future__ import annotations
import asyncio
from typing import Callable, Dict, Tuple, List, Optional
from builtins import enumerate, reversed
from .Class import (Message, Update, User, Components, RemoveMenuKeyboard, Chat, Price, ChatMember, HTTPClient, Updater,
                  Photo, Document, Location, ContactMessage, Video, Audio, NotFound, InvalidToken)

__all__ = (
    "Bot"
)


class _Loop:
    __slots__ = ()

    def __getattr__(self, key):
        raise AttributeError((
            
        ))

_loop = _Loop()


class Bot:
    
    __slots__ = (
        "loop",
        "token",
        "loop",
        "events",
        "listeners",
        "_user",
        "http",
        "_closed",
        "updater"
    )

    def __init__(self, token: str, **kwargs):
        if not isinstance(token, str):
            raise InvalidToken("token must be type of the str")
        self.loop = _loop
        self.token = token
        self.http: HTTPClient = HTTPClient(self.loop, token)
        self._user = None
        self.events: Dict[str, List[Callable]] = {}
        self.listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}
        self._closed = False

        self.updater: Updater = kwargs.get("updater", Updater)(self)

    def listen(self, event_name):
        return lambda func: self.addEvent(event_name, func)

    def addEvent(self, event: str, function):
        if not asyncio.iscoroutinefunction(function):
            raise TypeError(f"{function.__name__} is not a Coroutine Function")

        if not self.events.get(event):
            self.events[event] = list()

        self.events[event].append(function)

    def removeEvent(self, event: str, function=None):
        result = self.events.get(event)
        if not result:
            raise TypeError(f"{event} not in Events")

        if not function:
            del self.events[event]
            return

        if not function in result:
            raise TypeError(f"{function.__name__} not in Event Functions")

        del self.events[event][function]

    def wait_for(self, event_name: str, *, check=None, timeout=None):
        self.loop: asyncio.AbstractEventLoop
        future = self.loop.create_future()
        event_name = event_name.lower()
        if not check:
            check = lambda *args: True

        listeners = self.listeners.get(event_name)
        if not listeners:
            listeners = []
            self.listeners[event_name] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout=timeout)

    @property
    def user(self) -> Optional["User"]:
        return self._user

    async def setupHook(self):
        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop
        await self.http.start()

    async def __aenter__(self):
        await self.setupHook()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def close(self):
        await self.http.close()
        await self.updater.stop()
        self._closed = True

    def is_closed(self):
        return self._closed

    async def run_event(self, core, event_name, *args, **kwargs):
        try:
            await core(*args, **kwargs)
        except Exception as ext:
            await self.on_error(event_name, ext)

    def call_to_run_event(self, core, event_name, *args, **kwargs):
        task = self.run_event(core, event_name, *args, **kwargs)
        self.loop: asyncio.AbstractEventLoop
        return self.loop.create_task(task, name=f"python-bale-bot: {event_name}")

    def dispatch(self, event_name, /, *args, **kwargs):
        method = "on_" + event_name
        listeners = self.listeners.get(event_name)
        if listeners:
            removed = []
            for index, (future, check) in enumerate(listeners):
                if future.cancelled():
                    removed.append(index)
                    continue
                try:
                    result = check(*args)
                except Exception as __exception:
                    future.set_exception(__exception)
                    removed.append(index)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(index)

            if len(listeners) == len(removed):
                self.listeners.pop(event_name)
            else:
                for index in reversed(removed):
                    del listeners[index]

        events_core = self.events.get(method)
        if events_core:
            for event_core in events_core:
                self.call_to_run_event(event_core, method, *args, **kwargs)

    async def on_error(self, event_name, error):
        print("error", event_name, error)

    async def getBot(self) -> User:
        
        response = await self.http.getBot()
        return User.from_dict(data=response.result, bot=self)

    async def delete_webhook(self) -> bool:
        
        response = await self.http.delete_webhook()
        return response.result or False

    async def sendMessage(self, chat_id: str | int, text: str, *,
                           components: Optional["Components" | "RemoveMenuKeyboard"] = None,
                           reply_to_message_id: Optional[str | int] = None) -> "Message":
       
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if components:
            if not isinstance(components, (Components, RemoveMenuKeyboard)):
                raise TypeError(
                    "components param must be type of Components or RemoveComponents"
                )
            components = components.to_dict()

        if reply_to_message_id and not isinstance(reply_to_message_id, (int, str)):
            raise TypeError(
                "reply_to_message_id param must be type of Message"
            )

        response = await self.http.sendMessage(str(chat_id), text, components=components,
                                                reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def forwardMessage(self, chat_id: int | str, from_chat_id: int | str, message_id: int | str):
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(from_chat_id, (Chat, User)):
            raise TypeError(
                "from_chat_id param must be type of str or int"
            )

        if not isinstance(message_id, Message):
            raise TypeError(
                "message_id param must be type of str or int"
            )

        response = await self.http.forwardMessage(str(chat_id), str(from_chat_id), str(message_id))
        return Message.from_dict(data=response.result, bot=self)

    async def sendDocument(self, chat_id: str | int, document: bytes | str | "Document", *,
                            caption: Optional[str] = None,
                            reply_to_message_id: Optional[str | int] = None) -> "Message":
        
        if not isinstance(chat_id, (Chat, User)):
            raise TypeError(
                "chat_id param must be type of Chat or User"
            )

        if not isinstance(document, (bytes, str, Document)):
            raise TypeError(
                "document param must be type of bytes, str or Document"
            )

        if reply_to_message_id and not isinstance(reply_to_message_id, Message):
            raise TypeError(
                "reply_to_message_id param must be type of Message"
            )

        if isinstance(document, Document):
            document = document.file_id

        response = await self.http.sendDocument(chat_id, document, caption=caption,
                                                 reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def sendPhoto(self, chat_id: str | int, photo: bytes | str | "Photo", *, caption: Optional[str] = None,
                         reply_to_message_id: Optional[str | int] = None) -> "Message":
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(photo, (bytes, str, Photo)):
            raise TypeError(
                "photo param must be type of bytes, str or Photo"
            )

        if isinstance(photo, Photo):
            photo = photo.file_id

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        response = await self.http.sendPhoto(str(chat_id), photo, caption=caption,
                                              reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def sendAudio(self, chat_id: str | int, audio: bytes | str | "Audio", *, caption: Optional[str] = None,
                         reply_to_message_id: Optional[str | int] = None) -> "Message":
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(audio, (bytes, str, Audio)):
            raise TypeError(
                "audio param must be type of bytes, str or Audio"
            )

        if isinstance(audio, Audio):
            audio = audio.file_id

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        response = await self.http.sendAudio(str(chat_id), audio, caption=caption,
                                              reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def sendVideo(self, chat_id: str | int, video: bytes | str | "Photo", *, caption: Optional[str] = None,
                         reply_to_message_id: Optional[str | int] = None) -> "Message":
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(video, (bytes, str, Video)):
            raise TypeError(
                "video param must be type of bytes, str or Video"
            )

        if isinstance(video, Video):
            video = video.file_id

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        response = await self.http.sendVideo(str(chat_id), video, caption=caption,
                                              reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def sendLocation(self, chat_id: str | int, location: "Location") -> "Message":
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(location, Location):
            raise TypeError(
                "location param must be type of Location"
            )

        response = await self.http.sendLocation(str(chat_id), location.latitude, location.longitude)
        return Message.from_dict(data=response.result, bot=self)

    async def sendContact(self, chat_id: str | int, contact: "ContactMessage") -> "Message":
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat param must be type of str or int"
            )

        if not isinstance(contact, ContactMessage):
            raise TypeError(
                "contact param must be type of ContactMessage"
            )

        response = await self.http.sendContact(str(chat_id), contact.phone_number, contact.first_name,
                                                last_name=contact.last_name)
        return Message.from_dict(data=response.result, bot=self)

    async def sendVoice(self, chat_id: str | int, title: str, description: str, provider_token: str,
                           prices: List["Price"], *,
                           photo_url: Optional[str] = None, need_name: Optional[bool] = False,
                           need_phone_number: Optional[bool] = False,
                           need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False,
                           is_flexible: Optional[bool] = True) -> Message:
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat param must be type of str or int"
            )

        if not isinstance(title, str):
            raise TypeError(
                "title param must be type of str"
            )

        if not isinstance(provider_token, str):
            raise TypeError(
                "provider_token param must be type of str"
            )

        if not isinstance(prices, list):
            raise TypeError(
                "prices must param must be type of list"
            )

        if photo_url and not isinstance(photo_url, str):
            raise TypeError(
                "photo_url param must be type of str"
            )

        if need_name is not None and not isinstance(need_name, bool):
            raise TypeError(
                "need_name param must be type of boolean"
            )

        if need_phone_number is not None and not isinstance(need_phone_number, bool):
            raise TypeError(
                "need_phone_number param must be type of boolean"
            )

        if need_email is not None and not isinstance(need_email, bool):
            raise TypeError(
                "need_email param must be type of boolean"
            )

        if need_shipping_address is not None and not isinstance(need_shipping_address, bool):
            raise TypeError(
                "need_shipping_address param must be type of boolean"
            )

        if is_flexible is not None and not isinstance(is_flexible, bool):
            raise TypeError(
                "is_flexible param must be type of boolean"
            )

        prices = [price.to_dict() for price in prices if isinstance(price, Price)]
        response = await self.http.sendVoice(str(chat_id), title, description, provider_token, prices, photo_url,
                                                need_name,
                                                need_phone_number, need_email, need_shipping_address, is_flexible)
        return Message.from_dict(data=response.result, bot=self)

    async def editMessage(self, chat_id: str | int, message_id: str | int, text: str, *,
                           components: Optional["Components" | "RemoveMenuKeyboard"] = None) -> "Message":
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(message_id, (str, int)):
            raise TypeError(
                "message_id param must be type of str or int"
            )

        if components and not isinstance(components, (Components, RemoveMenuKeyboard)):
            raise TypeError(
                "components param must be type of Components or RemoveComponents"
            )

        if components:
            components = components.to_dict()

        response = await self.http.editMessage(chat_id, message_id, text, components=components)
        return response.result

    async def deleteMessage(self, chat_id: str | int, message_id: str | int) -> bool:
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(message_id, (str, int)):
            raise TypeError(
                "message_id param must be type of str or int"
            )
        response = await self.http.deleteMessage(str(chat_id), message_id)
        return response.result or False

    async def getChat(self, chat_id: int | str) -> Chat | None:
        
        if not isinstance(chat_id, (int, str)):
            raise TypeError(
                "chat_id param must be type of int or str"
            )

        try:
            response = await self.http.getChat(str(chat_id))
        except NotFound:
            return None
        else:
            return Chat.from_dict(response.result, bot=self)

    async def get_user(self, user_id: int | str) -> "User" | None:
       
        if not isinstance(user_id, (int, str)):
            raise TypeError(
                "user_id param must be type of int or str"
            )

        chat = await self.getChat(user_id)
        if chat and chat.type.is_private_chat():
            return User.from_dict(chat.to_dict(), self)

        return None

    async def getChatMember(self, chat_id: str | int, user_id: str | int) -> "ChatMember" | None:
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat param must be type of Chat"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id must be type of str or int"
            )

        try:
            response = await self.http.getChatMember(chat_id=str(chat_id), member_id=str(user_id))
        except NotFound:
            return None
        else:
            return ChatMember.from_dict(chat_id, response.result, self)

    async def banChatMember(self, chat_id: str | int, user_id: str | int) -> "ChatMember":
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id must be type of str or int"
            )

        response = await self.http.banChatMember(chat_id=str(chat_id), member_id=str(user_id))
        return response.result

    async def getChatMembersCount(self, chat_id: str | int) -> int:
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        response = await self.http.getChatMembersCount(str(chat_id))
        return response.result

    async def getChatAdministrators(self, chat_id: str | int) -> list["ChatMember"] | None:
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        response = await self.http.getChatAdministrators(chat_id)
        return [ChatMember.from_dict(chat_id=chat_id, data=member_payload, bot=self) for member_payload in response.result or list()]

    async def getFile(self, file_id: str):
        
        if not isinstance(file_id, str):
            raise TypeError(
                "file_id must be type of str"
            )

        return await self.http.getFile(file_id)

    async def invite_user(self, chat_id: str | int, user_id: str | int) -> bool:
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id param must be type of str or int"
            )

        response = await self.http.invite_to_chat(str(chat_id), str(user_id))
        return response.result or False

    async def leaveChat(self, chat_id: str | int) -> bool:
        
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )
        response = await self.http.leaveChat(str(chat_id))
        return response.result or False

    async def getUpdates(self, offset: int = None, limit: int = None) -> list["Update"]:
        if offset and not isinstance(offset, int):
            raise TypeError(
                "offset param must be int"
            )

        if limit and not isinstance(limit, int):
            raise TypeError(
                "limit param must be int"
            )

        response = await self.http.getUpdates(offset, limit)
        return [Update.from_dict(data=update_payload, bot=self) for update_payload in response.result
                if not offset or (offset and update_payload.get("update_id") > offset)] if response.result else None

    async def connect(self, sleep_after_every_get_updates):
        self._user = await self.getBot()
        await self.updater.start(sleep_after_every_get_updates=sleep_after_every_get_updates)

    def run(self, sleep_after_every_get_updates=None):

        async def main():
            async with self:
                await self.connect(sleep_after_every_get_updates=sleep_after_every_get_updates)

        try:
            asyncio.run(main())
        except KeyboardInterrupt:  # Control-C
            pass
        except SystemExit:
            pass
