import sys
import time
import telepot

from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup
from ChatHandler import PrivateUserChat
from TelegramUser import TChat

TOKEN = sys.argv[1]  # get token from command-line
TIMEOUT = 60
bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, PrivateUserChat, timeout=TIMEOUT)
    # pave_event_space()(
    #     per_chat_id(types='private'), create_open, PrivateUserChat, timeout=TIMEOUT),
    # pave_event_space()(
    #     per_chat_id(types=['supergroup', 'group']), create_open, GroupChat, timeout=TIMEOUT),
])
MessageLoop(bot).run_as_thread()

TChat.bot = bot

while 1:
    time.sleep(10)