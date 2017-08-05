
import sys
import telepot


from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup

from .ChatHandler import PrivateUserChat
from .TelegramUser import TChat
from .CommandsBase import BaseCommand, PatternCommand, HandledStatus, ChatType, KeyboardCommand

from .Tools import *

def Start(telegram_bot_token, thread_timeout = 60):
    bot = telepot.DelegatorBot(telegram_bot_token, [
        pave_event_space()(
            per_chat_id(), create_open, PrivateUserChat, timeout=thread_timeout)
        # pave_event_space()(
        #     per_chat_id(types='private'), create_open, PrivateUserChat, timeout=TIMEOUT),
        # pave_event_space()(
        #     per_chat_id(types=['supergroup', 'group']), create_open, GroupChat, timeout=TIMEOUT),
    ])
    MessageLoop(bot).run_as_thread()

    TChat.bot = bot
    TChat.bot_username = TChat.bot.getMe()["username"]
    print(TChat.bot.getMe())
    
if __name__ == '__main__':
    TOKEN = sys.argv[1]  # get token from command-line
    TIMEOUT = 60
    Start(TOKEN,TIMEOUT)