"""Launch the bot using MessageLoop."""
import os
import sys
import time
import telepot
# import ledController as led
import tempfile
from .TelegramUser import TUser, TGroup, TChat
from .CommandsBase import redirect_msg

from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup
# from BotMock import User, Chat
# from BDMock import BDWrapper
# from RadioPlayer import FmPlayer


class MessageCounter(telepot.helper.ChatHandler):
    """
    Sample class to show how to use ChatHandler.
    Is no being used.
    """

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

    def on__idle(self, event):
        """Do something on idle"""
        self.sender.sendMessage("dispose")
        super().on__idle(event)


class PrivateUserChat(telepot.helper.ChatHandler):
    """Handles the private msgs"""

    def __init__(self, *args, **kwargs):
        super(PrivateUserChat, self).__init__(*args, **kwargs)
        # TelegramUser.TUser.bot = self.bot

    def open(self, initial_msg, seed):
        """Do something when the first msg arrives."""
        pass
    def on_chat_message(self, msg):
        """handle new msg."""
        # self._user.update_telegram_user(msg["from"])
        if msg["chat"]["id"] != msg["from"]["id"]:
            self.chat = TGroup(msg["chat"])
            self.user = TUser(msg["from"])
        else:
            self.chat = TChat(msg["chat"])
            self.user = TUser(msg["from"])
        try:
            redirect_msg(msg, self.user, self.chat)
        except telepot.exception.TelegramError as err:
            print(err)

    def on__idle(self, event):
        """Do something on idle"""
        # call base class on_idle to rise an exception and stop the thread
        super().on__idle(event)


class GroupChat(telepot.helper.ChatHandler):

    """DEPRECATED: Handles the group msgs"""

    def __init__(self, *args, **kwargs):
        super(GroupChat, self).__init__(*args, **kwargs)
        self._users = list()

    def open(self, initial_msg, seed):
        """Do something when the first msg arrives."""
       # self.sender.sendMessage("Welcome to this group chat")
        # self._chat = Chat.create_chat_by_id(initial_msg["chat"])

    def on_chat_message(self, msg):
        """handle new msg."""
        pass
        # for user in _users:
        # self._chat.update_chat(msg["chat"])
        # self._chat.add_user(msg["from"])
        # current_user = self.add_user_to_group_list(msg["from"])
        # if current_user.checkForPrivileges("User"):
        #     if "voice" in msg:
        #         voiceFile = self.bot.getFile(msg["voice"]["file_id"])
        #         self.sender.sendMessage(
        #             "Playing your audio over radio at " + str(FmPlayer.freq) + " Hz")
        #         self.bot.download_file(
        #             voiceFile["file_id"], "voice/" + str(voiceFile["file_id"]) + ".ogg")
        #         FmPlayer.play_file(
        #             "voice/" + str(voiceFile["file_id"]) + ".ogg")
        # if "text" in msg:
        # if msg["text"] == "/led":
        #     self.sender.sendMessage(
        #         'Here are the led controllers',
        #         reply_markup=ReplyKeyboardMarkup(
        #             resize_keyboard=True,
        #             keyboard=[[
        #                 KeyboardButton(text='LED ON'),
        #                 KeyboardButton(text='LED OFF'),
        #             ]]
        #         )
        #     )
        # if msg["text"] == "/on" or msg["text"] == "LED ON":
        #     led.on()
        #     self.sender.sendMessage("Led ON")
        # if msg["text"] == "/off" or msg["text"] == "LED OFF":
        #     led.off()
        #     self.sender.sendMessage("Led OFF")

    # def add_user_to_group_list(self, user_msg):
    #     for user in self._users:
    #         if user.id() == user_msg["id"]:
    #             user.update_telegram_user(user_msg)
    #             return user
    #     new_user = User.create_user_by_Id(user_msg)
    #     new_user.add_group(self.chat_id)
    #     self._users.append(new_user)
    #     return new_user

    # def on_close(self, event):
    #     """Do something on close"""
    #     print("closed")
    #     self.sender.sendMessage("closed")
    #     telepot.helper.ChatHandler.on_close(self,event)

    def on__idle(self, event):
        """Do something on idle"""
#        self.sender.sendMessage("dispose")
        # Chat.dispose_chat_by_id(self.chat_id)
        # for user in self._users:
        # User.dispose_user_by_id(user.id())
        super().on__idle(event)


# TOKEN = sys.argv[1]  # get token from command-line
# TIMEOUT = 60
# bot = telepot.DelegatorBot(TOKEN, [
#     pave_event_space()(
#         per_chat_id(), create_open, PrivateUserChat, timeout=TIMEOUT)
#     # pave_event_space()(
#     #     per_chat_id(types='private'), create_open, PrivateUserChat, timeout=TIMEOUT),
#     # pave_event_space()(
#     #     per_chat_id(types=['supergroup', 'group']), create_open, GroupChat, timeout=TIMEOUT),
# ])
# MessageLoop(bot).run_as_thread()

# while 1:
#     time.sleep(10)
