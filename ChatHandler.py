import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from BotMock import User
from BDMock import BDWrapper

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
        self.sender.sendMessage("Welcome to this private chat")
        self._user = User.create_user_by_Id(initial_msg["from"])

    def on_chat_message(self, msg):
        """handle new msg.""" 
        if msg["text"] == "/User":
            self._user.privileges.add("User")
        if msg["text"] == "/CanI":
            self.sender.sendMessage(self._user.checkForPrivileges("User"))
        self.sender.sendMessage(self._user.get_last_msg())
        self._user.set_last_msg(msg["text"])
        

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
        self._count = 0

    def open(self, initial_msg, seed):
        """Do something when the first msg arrives."""
        self.sender.sendMessage("Welcome to this group chat")
        self._user = User.create_user_by_Id(initial_msg["from"]["id"])

    def on_chat_message(self, msg):
        """handle new msg.""" 
        self._count += 1
        self.sender.sendMessage(self._count)
        self.sender.sendMessage(self._user.get_last_msg())
        self._user.set_last_msg(msg["text"]) 
        

    # def on_close(self, event):
    #     """Do something on close"""
    #     print("closed")
    #     self.sender.sendMessage("closed")
    #     telepot.helper.ChatHandler.on_close(self,event)

    def on__idle(self,event):
        """Do something on idle"""
        self.sender.sendMessage("dispose")
        User.dispose_user_by_id(self.chat_id)
        telepot.helper.IdleTerminateMixin.on__idle(self,event)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(types='private'), create_open, PrivateUserChat, timeout=5),
    pave_event_space()(
        per_chat_id(types='group'), create_open, GroupChat, timeout=5),
])
MessageLoop(bot).run_as_thread()

while 1:
    time.sleep(10)