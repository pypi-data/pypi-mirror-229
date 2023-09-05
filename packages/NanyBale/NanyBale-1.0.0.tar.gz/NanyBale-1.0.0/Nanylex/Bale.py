import asyncio
import aiohttp
from json import dumps
from .message import Message

class Bale:
    
    def __init__(self, token: str):
        self.token = token

    async def makeRequests(self, method: str, data: dict = None, params: dict = None):
        url = f'https://tapi.bale.ai/bot{self.token}/{method}'
        async with aiohttp.ClientSession() as X:
            async with X.post(url=url,data=data,params=params) as xco:
                return await xco.json()

    def sendReq(self, method: str, data: dict = None, params: dict = None):
        try:
            return asyncio.run(self.makeRequests(method,data,params))
        except:pass

    def getChatUpdate(self):
        print(f'\033[94mConnecting To Server...')
        params_form = {'offset':0,'limit':99999999999999999999}
        while True:
            resone = self.sendReq('getupdates',params=params_form)
            params_form['offset'] = 1
            if resone != None and resone['ok'] == True and resone['result'] != []:
                break
        params_form['offset'] = resone['result'][len(resone['result'])-1]['update_id'] + 1
        params_form['limit'] = 1
        print(f'\033[92mConected\033[00m')
        while True:
            res = self.sendReq('getupdates',params=params_form)
            if res != None and res['result'] != []:
                params_form['offset'] += 1
                yield Message(res['result'][0])

    def getChatByUpdateID(self, offset: int, limit: int):
        params_form = {'offset':offset,'limit':limit}
        return self.sendReq('getupdates',params=params_form)
     
    def getMe(self):
        return self.sendReq('getMe')
    
    def getFile(self,file_id: str):
        params_form = {'file_id':file_id}
        return self.sendReq('getfile',params=params_form)
    
    def getChat(self,chat_id: str):
        params_form = {'chat_id':chat_id}
        return self.sendReq('getchat',params=params_form)
    
    def getChatAdministrators(self,chat_id: str):
        params_form = {'chat_id':chat_id}
        return self.sendReq('getChatAdministrators',params=params_form)
    
    def getChatMembersCount(self,chat_id: str):
        params_form = {'chat_id':chat_id}
        return self.sendReq('getChatMembersCount',params=params_form)
    
    def getChatMember(self,chat_id: str, user_id: str):
        params_form = {'chat_id':chat_id,'user_id':user_id}
        return self.sendReq('getChatMember',params=params_form)
    
    def banChatMember(self, chat_id: str, user_id: str):
        data_form = {'chat_id':chat_id,'user_id':user_id}
        return self.sendReq('banChatMember',data=dumps(data_form))
    
    def editMessageText(self, chat_id: str, text: str, message_id: str):
        data_form = {'chat_id':chat_id,'message_id':message_id,'text':text}
        return self.sendReq('EditMessageText',data=dumps(data_form))
    
    def deleteMessage(self, chat_id: str, message_id: str):
        data_form = {'chat_id':chat_id,'message_id':message_id}
        return self.sendReq('deletemessage',data=dumps(data_form))
    
    def forwardMessage(self, chat_id: str, from_chat_id: str, message_id: str):
        data_form = {'chat_id':chat_id,'from_chat_id':from_chat_id,'message_id':message_id}
        return self.sendReq('ForwardMessage',data=dumps(data_form))
    
    def sendMessage(self, chat_id: str, text: str, reply_message_id: str = None, inline_keyboard: dict = None, keyboard: dict = None):
        data_form = {'chat_id':chat_id,'text':text}
        if inline_keyboard != None : data_form['reply_markup'] = {'inline_keyboard':inline_keyboard}
        if keyboard != None : data_form['reply_markup'] = {'keyboard':keyboard}
        if reply_message_id != None : data_form['reply_to_message_id'] = reply_message_id
        return self.sendReq('sendMessage',data=dumps(data_form))
    
    def sendLocation(self, chat_id: str, latitude: str, longitude: str, reply_message_id: str = None):
        data_form = {'chat_id':chat_id,'latitude':latitude,'longitude':longitude}
        if reply_message_id != None : data_form['reply_to_message_id'] = reply_message_id
        return self.sendReq('sendLocation',data=dumps(data_form))
    
    def leaveChat(self, chat_id: str):

        self.sendReq("leaveChat", params={"chat_id": chat_id})
    
    def sendContact(self, chat_id: str, phone_number: str, first_name: str, last_name: str = None, reply_message_id: str = None):
        data_form = {'chat_id':chat_id,'phone_number':phone_number,'first_name':first_name}
        if last_name != None : data_form['last_name'] = last_name
        if reply_message_id != None : data_form['reply_to_message_id'] = reply_message_id
        return self.sendReq('sendContact',data=dumps(data_form))
    
    def sendPhoto(self, chat_id: str, photo: str, text: str = None, reply_message_id: str = None):
        data_form = aiohttp.FormData()
        file = photo if 'http' in photo else open(photo,'rb')
        data_form.add_field('chat_id',str(chat_id))
        data_form.add_field('photo',file)
        if text != None : data_form.add_field('caption',text)
        if reply_message_id != None : data_form.add_field('reply_to_message_id',str(reply_message_id))
        return self.sendReq('SendPhoto',data=data_form)
    
    def sendAudio(self, chat_id: str, audio: str, text: str = None, duration: str = None, title: str = None, reply_message_id: str = None):
        data_form = aiohttp.FormData()
        file = audio if 'http' in audio else open(audio,'rb')
        data_form.add_field('chat_id',str(chat_id))
        data_form.add_field('audio',file)
        if text != None : data_form.add_field('caption',text)
        if duration != None : data_form.add_field('duration',duration)
        if title != None : data_form.add_field('title',audio)
        if reply_message_id != None : data_form.add_field('reply_to_message_id',str(reply_message_id))
        return self.sendReq('SendAudio',data=data_form)
    
    def sendDocument(self, chat_id: str, document: str, text: str = None, reply_message_id: str = None):
        data_form = aiohttp.FormData()
        file = document if 'http' in document else open(document,'rb')
        data_form.add_field('chat_id',str(chat_id))
        data_form.add_field('document',file)
        if text != None : data_form.add_field('caption',text)
        if reply_message_id != None : data_form.add_field('reply_to_message_id',str(reply_message_id))
        return self.sendReq('SendDocument',data=data_form)
    
    def sendVideo(self, chat_id: str, video: str, text: str = None, reply_message_id: str = None):
        data_form = aiohttp.FormData()
        file = video if 'http' in video else open(video,'rb')
        data_form.add_field('chat_id',str(chat_id))
        data_form.add_field('video',file)
        if text != None : data_form.add_field('caption',text)
        if reply_message_id != None : data_form.add_field('reply_to_message_id',str(reply_message_id))
        return self.sendReq('SendVideo',data=data_form)
    
    def sendVoice(self, chat_id: str, voice: str, text: str = None, reply_message_id: str = None):
        data_form = aiohttp.FormData()
        file = voice if 'http' in voice else open(voice,'rb')
        data_form.add_field('chat_id',str(chat_id))
        data_form.add_field('voice',file)
        if text != None : data_form.add_field('caption',text)
        if reply_message_id != None : data_form.add_field('reply_to_message_id',str(reply_message_id))
        return self.sendReq('SendVoice',data=data_form)

    def resendFile(self, type: str, chat_id: str, file_id: str, text: str = None, reply_message_id: str = None):
        data_form = {'chat_id':chat_id,type:file_id}
        if text != None : data_form['caption'] = text
        if reply_message_id != None : data_form['reply_to_message_id'] = reply_message_id
        if type == 'document':
            return self.sendReq('SendDocument',data=dumps(data_form))
        elif type == 'photo':
            return self.sendReq('SendPhoto',data=dumps(data_form))
        elif type == 'audio':
            return self.sendReq('SendAudio',data=dumps(data_form))
        elif type == 'video':
            return self.sendReq('SendVideo',data=dumps(data_form))
        elif type == 'voice':
            return self.sendReq('SendVoice',data=dumps(data_form))