import os
import sys
import time
import telepot
import ledController as led
import tempfile

from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from BotMock import User, Chat
from BDMock import BDWrapper
from RadioPlayer import FmPlayer

#BDWrapper.createDBConnection()

class MessageCounter(telepot.helper.ChatHandler):
    """Sample class to show how to use ChatHandler."""
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0

    def open(self, initial_msg, seed):
        """Do something when the first msg arrives."""
        self.sender.sendMessage("Welcome")

    def on_chat_message(self, msg):
        """handle new msg.""" 
        self._count += 1
        self.sender.sendMessage(self._count)
        self.sender.sendMessage(msg)

    # def on_close(self, event):
    #     """Do something on close"""
    #     print("closed")
    #     self.sender.sendMessage("closed")
    #     telepot.helper.ChatHandler.on_close(self,event)

    def on__idle(self,event):
        """Do something on idle"""
        self.sender.sendMessage("dispose")
        telepot.helper.IdleTerminateMixin.on__idle(self,event)


class PrivateUserChat(telepot.helper.ChatHandler):
    """Handles the private msgs"""
    def __init__(self, *args, **kwargs):
        super(PrivateUserChat, self).__init__(*args, **kwargs)

    def open(self, initial_msg, seed):
        """Do something when the first msg arrives."""
        self._user = User.create_user_by_Id(initial_msg["from"])
#        self.sender.sendMessage("Welcome to this private chat")

    def on_chat_message(self, msg):
        """handle new msg.""" 
        self._user.update_telegram_user(msg["from"])
        try:
            if "voice" in msg: 
                voiceFile = self.bot.getFile(msg["voice"]["file_id"])
                self.sender.sendMessage("Playing your audio over radio")
                self.bot.download_file(voiceFile["file_id"],"voice/" + str(voiceFile["file_id"]) + ".wav")
                FmPlayer.play_file("voice/" + str(voiceFile["file_id"]) + ".wav")
            if "text" in msg:
                if msg["text"] == "Star":
                    self.sender.sendMessage("may the force be with you")
                    os.system("sudo ~/fm_transmitter/fm_transmitter -f 108.0 -r ~/fm_transmiter/star_wars.wav")
                if msg["text"] == "/User":
                    self._user.privileges.add("User")
                    self.sender.sendMessage("You are user now")
                if msg["text"].startswith("/Admin"):
                    if msg["text"].endswith("erni"):
                        self._user.privileges.add("Admin")
                        self.sender.sendMessage("You are admin now")
                    else:
                        self.sender.sendMessage("Wrong password")

                if msg["text"] == "/CanI":
                    self.sender.sendMessage(",".join(self._user.privileges))
                if msg["text"] == "/toGroup":
                    for groupId in self._user.groups:
                        self.bot.sendMessage(groupId,str(self._user._telegram_user["username"]))

                self.sender.sendMessage(self._user.get_last_msg() +".")
                self._user.set_last_msg(msg["text"])
        
        except telepot.exception.TelegramError as err:
            print(err)
            pass


        

    # def on_close(self, event):
    #     """Do something on close"""
    #     print("closed")
    #     telepot.helper.ChatHandler.on_close(self,event)

    def on__idle(self,event):
        """Do something on idle"""
        self.sender.sendMessage("closed")
        User.dispose_user_by_id(self.chat_id)
        telepot.helper.IdleTerminateMixin.on__idle(self,event)




class GroupChat(telepot.helper.ChatHandler):
    
    """Handles the group msgs"""
    def __init__(self, *args, **kwargs):
        super(GroupChat, self).__init__(*args, **kwargs)
        self._users = list()

    def open(self, initial_msg, seed):
        """Do something when the first msg arrives."""
       # self.sender.sendMessage("Welcome to this group chat")
        self._chat = Chat.create_chat_by_id(initial_msg["chat"])

    def on_chat_message(self, msg):
        """handle new msg.""" 
        #for user in _users:
        self._chat.update_chat(msg["chat"])
        self._chat.add_user(msg["from"])
        current_user = self.add_user_to_group_list(msg["from"])
        if current_user.checkForPrivileges("User"):
            if msg["text"] == "/on":
                led.on()
                self.sender.sendMessage("Led ON")
            if msg["text"] == "/off":
                led.off()    
                self.sender.sendMessage("Led OFF")
        
    def add_user_to_group_list(self, user_msg):
        for user in self._users:
            if user.id() == user_msg["id"]:
                user.update_telegram_user(user_msg)
                return user
        new_user = User.create_user_by_Id(user_msg)
        new_user.add_group(self.chat_id)
        self._users.append(new_user)
        return new_user

    # def on_close(self, event):
    #     """Do something on close"""
    #     print("closed")
    #     self.sender.sendMessage("closed")
    #     telepot.helper.ChatHandler.on_close(self,event)

    def on__idle(self,event):
        """Do something on idle"""
#        self.sender.sendMessage("dispose")
        Chat.dispose_chat_by_id(self.chat_id)
        for user in self._users:
            User.dispose_user_by_id(user.id())
        telepot.helper.IdleTerminateMixin.on__idle(self,event)


TOKEN = sys.argv[1]  # get token from command-line
TIMEOUT = 60
bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(types='private'), create_open, PrivateUserChat, timeout=TIMEOUT),
    pave_event_space()(
        per_chat_id(types=['supergroup','group']), create_open, GroupChat, timeout=TIMEOUT),
])
MessageLoop(bot).run_as_thread()

while 1:
    time.sleep(10)